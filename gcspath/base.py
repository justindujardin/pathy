from pathlib import PurePath, _PosixFlavour  # noqa
from typing import Iterable, Optional, Union, List, Generator

try:
    import google.cloud.storage  # noqa

    has_gcs = True
except ImportError:
    has_gcs = False


class _GCSFlavour(_PosixFlavour):
    is_supported = bool(has_gcs)

    def parse_parts(self, parts):
        drv, root, parsed = super().parse_parts(parts)
        for part in parsed[1:]:
            if part == "..":
                index = parsed.index(part)
                parsed.pop(index - 1)
                parsed.remove(part)
        return drv, root, parsed

    def make_uri(self, path):
        uri = super().make_uri(path)
        return uri.replace("file:///", "gs://")


_gcs_flavour = _GCSFlavour()


class PureGCSPath(PurePath):
    """
    PurePath subclass for GCS service.

    GCS is not a file-system but we can look at it like a POSIX system.
    """

    _flavour = _gcs_flavour
    __slots__ = ()

    @classmethod
    def from_uri(cls, uri):
        """
        from_uri class method create a class instance from url

        >> from gcspath import PureGCSPath
        >> PureGCSPath.from_url('gs://<bucket>/')
        << PureGCSPath('/<bucket>')
        """
        if not uri.startswith("gs://"):
            raise ValueError("...")
        return cls(uri[4:])

    @property
    def bucket(self):
        """
        bucket property
        return a new instance of only the bucket path
        """
        self._absolute_path_validation()
        if not self.is_absolute():
            raise ValueError("relative path don't have bucket")
        try:
            _, bucket, *_ = self.parts
        except ValueError:
            return None
        return type(self)(self._flavour.sep, bucket)

    @property
    def key(self):
        """
        bucket property
        return a new instance of only the key path
        """
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key:
            return None
        return type(self)(key)

    def as_uri(self):
        """
        Return the path as a 'gs' URI.
        """
        return super().as_uri()

    @property
    def bucket_name(self) -> str:
        return str(self.bucket)[1:]

    @property
    def prefix(self) -> str:
        sep = self._flavour.sep
        if not self.key:
            return ""
        key_name = str(self.key)
        if not key_name.endswith(sep):
            return key_name + sep
        return key_name

    def _absolute_path_validation(self):
        if not self.is_absolute():
            raise ValueError("relative path has no bucket/key specification")
