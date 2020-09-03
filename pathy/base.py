import io
from pathlib import _PosixFlavour  # type:ignore
from pathlib import PurePath
from typing import List, TypeVar, Union

PathType = TypeVar("PathType")

StreamableType = Union[io.TextIOWrapper, io.FileIO, io.BytesIO]


class _GCSFlavour(_PosixFlavour):
    is_supported = True

    def parse_parts(self, parts: List[str]):
        drv, root, parsed = super().parse_parts(parts)
        if len(parsed) and parsed[0].endswith(":"):
            if len(parsed) < 2:
                raise ValueError("need atleast two parts")
            # Restore the
            drv = parsed[0]  # scheme:
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


class PurePathy(PurePath):
    """PurePath subclass for bucket storage."""

    _flavour = _gcs_flavour
    __slots__ = ()

    @property
    def scheme(self) -> str:
        """Return the scheme portion of this path. A path's scheme is the leading
        few characters. In a website you would see a scheme of "http" or "https".

        Consider a few examples:

        ```python
        assert Pathy("gs://foo/bar").scheme == "gs"
        assert Pathy("file:///tmp/foo/bar").scheme == "file"

        """
        # This is an assumption of mine. I think it's fine, but let's
        # cause an error if it's not the case.
        assert self.drive[-1] == ":", "drive should end with :"
        return self.drive[:-1]

    @property
    def bucket(self: PathType) -> PathType:
        """Return a new instance of only the bucket path."""
        self._absolute_path_validation()
        return type(self)(f"{self.drive}//{self.root}")

    @property
    def key(self: PathType) -> "PathType":
        """Return a new instance of only the key path."""
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key or len(self.parts) < 2:
            return None
        return type(self)(key)

    @property
    def prefix(self: PathType) -> str:
        sep = self._flavour.sep
        str(self)
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
