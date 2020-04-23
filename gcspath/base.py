from pathlib import PurePath, _PosixFlavour  # noqa
from typing import TypeVar, List, Tuple
import os

try:
    import google.cloud.storage  # noqa

    has_gcs = True
except ImportError:
    has_gcs = False


PathType = TypeVar("PathType")


class _GCSFlavour(_PosixFlavour):
    is_supported = bool(has_gcs)

    def parse_parts(self, parts):
        drv, root, parsed = super().parse_parts(parts)
        if len(parsed) and parsed[0] == "gs:":
            if len(parsed) < 2:
                raise ValueError("need atleast two parts")
            # Restore the
            drv = parsed[0]  # gs:
            root = parsed[1]  # bucket_name
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

    @property
    def bucket(self):
        """
        bucket property
        return a new instance of only the bucket path
        """
        self._absolute_path_validation()
        return type(self)(f"{self.drive}//{self.root}")

    @property
    def key(self):
        """
        key property
        return a new instance of only the key path
        """
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key or len(self.parts) < 2:
            return None
        return type(self)(key)

    @property
    def prefix(self) -> str:
        sep = self._flavour.sep
        a = str(self)
        key = self.key
        if not key:
            return ""
        key_name = str(key)
        if not key_name.endswith(sep):
            return key_name + sep
        return key_name

    def _absolute_path_validation(self):
        if not self.is_absolute():
            raise ValueError("relative paths has no bucket/key specification")

    @classmethod
    def _format_parsed_parts(cls, drv, root, parts):
        # Bucket path "gs://foo/bar"
        if drv and root:
            return f"{drv}//{root}/" + cls._flavour.join(parts[2:])
        # Absolute path
        elif drv or root:
            return drv + root + cls._flavour.join(parts[1:])
        else:
            # Relative path
            return cls._flavour.join(parts)
