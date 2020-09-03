from dataclasses import dataclass
from io import DEFAULT_BUFFER_SIZE
from pathlib import _PosixFlavour  # type:ignore
from pathlib import Path, PurePath
from typing import IO, Any, Generator, List, Optional, Tuple, TypeVar, Union, cast

SUBCLASS_ERROR = "must be implemented in a subclass"
PathType = TypeVar("PathType", bound="BasePathy")
StreamableType = IO[Any]
FluidPath = Union["BasePathy", Path]


class _GCSFlavour(_PosixFlavour):
    is_supported = True

    def parse_parts(self, parts: List[str]) -> Tuple[str, str, List[str]]:
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

    def make_uri(self, path: PathType) -> str:
        uri = super().make_uri(path)
        return uri.replace("file:///", "gs://")


_gcs_flavour = _GCSFlavour()


@dataclass
class BlobStat:
    """Stat for a bucket item"""

    size: int
    last_modified: int


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
    def bucket(self) -> "BasePathy":
        """Return a new instance of only the bucket path."""
        self._absolute_path_validation()
        return cast(BasePathy, type(self)(f"{self.drive}//{self.root}"))

    @property
    def key(self) -> Optional["BasePathy"]:
        """Return a new instance of only the key path."""
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key or len(self.parts) < 2:
            return None
        return cast(BasePathy, type(self)(key))

    @property
    def prefix(self) -> str:
        sep = self._flavour.sep
        str(self)
        key = self.key
        if not key:
            return ""
        key_name = str(key)
        if not key_name.endswith(sep):
            return key_name + sep
        return key_name

    def _absolute_path_validation(self) -> None:
        if not self.is_absolute():
            raise ValueError("relative paths has no bucket/key specification")

    @classmethod
    def _format_parsed_parts(cls, drv: str, root: str, parts: List[str]) -> str:
        # Bucket path "gs://foo/bar"
        if drv and root:
            return f"{drv}//{root}/" + cls._flavour.join(parts[2:])
        # Absolute path
        elif drv or root:
            return drv + root + cls._flavour.join(parts[1:])
        else:
            # Relative path
            return cls._flavour.join(parts)


class BasePathy(Path, PurePathy):
    """Abstract base class for Pathy, which exists to help
    keep strong types flowing through the various clients."""

    __slots__ = ()
    _NOT_SUPPORTED_MESSAGE = "{method} is an unsupported bucket operation"

    def __truediv__(self, key: Union[str, Path, "BasePathy", PurePathy]) -> PathType:
        return super().__truediv__(key)  # type:ignore

    def __rtruediv__(self, key: Union[str, Path, "BasePathy", PurePathy]) -> PathType:
        return super().__rtruediv__(key)  # type:ignore

    def stat(self: PathType) -> BlobStat:
        return super().stat()  # type:ignore

    def exists(self: PathType) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def is_dir(self: PathType) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def is_file(self: PathType) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def iterdir(self: PathType) -> Generator[PathType, None, None]:
        yield from super().iterdir()  # type:ignore

    def glob(self: PathType, pattern: str) -> Generator[PathType, None, None]:
        yield from super().glob(pattern=pattern)  # type:ignore

    def rglob(self: PathType, pattern: str) -> Generator[PathType, None, None]:
        yield from super().rglob(pattern=pattern)  # type:ignore

    def open(
        self: PathType,
        mode: str = "r",
        buffering: int = DEFAULT_BUFFER_SIZE,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        raise NotImplementedError(SUBCLASS_ERROR)

    def owner(self: PathType) -> str:
        raise NotImplementedError(SUBCLASS_ERROR)

    def resolve(self: PathType, strict: bool = False) -> PathType:
        raise NotImplementedError(SUBCLASS_ERROR)

    def rename(self: PathType, target: Union[str, PurePath]) -> None:
        return super().rename(target)

    def replace(self: PathType, target: Union[str, PurePath]) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)

    def rmdir(self: PathType) -> None:
        return super().rmdir()

    def samefile(
        self: PathType, other_path: Union[str, bytes, int, Path, PathType]
    ) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def touch(self: PathType, mode: int = 0o666, exist_ok: bool = True) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)

    def mkdir(
        self: PathType, mode: int = 0o777, parents: bool = False, exist_ok: bool = False
    ) -> None:
        return super().mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def is_mount(self: PathType) -> bool:
        return False

    def is_symlink(self: PathType) -> bool:
        return False

    def is_socket(self: PathType) -> bool:
        return False

    def is_fifo(self: PathType) -> bool:
        return False

    # Unsupported operations below here

    @classmethod
    def cwd(cls) -> PathType:
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.cwd.__qualname__)
        raise NotImplementedError(message)

    @classmethod
    def home(cls) -> PathType:
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.home.__qualname__)
        raise NotImplementedError(message)

    def chmod(self: PathType, mode: int) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.chmod.__qualname__)
        raise NotImplementedError(message)

    def expanduser(self: PathType) -> PathType:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.expanduser.__qualname__
        )
        raise NotImplementedError(message)

    def lchmod(self: PathType, mode: int) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lchmod.__qualname__)
        raise NotImplementedError(message)

    def group(self: PathType) -> str:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.group.__qualname__)
        raise NotImplementedError(message)

    def is_block_device(self: PathType) -> bool:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_block_device.__qualname__
        )
        raise NotImplementedError(message)

    def is_char_device(self: PathType) -> bool:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_char_device.__qualname__
        )
        raise NotImplementedError(message)

    def lstat(self: PathType) -> BlobStat:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lstat.__qualname__)
        raise NotImplementedError(message)

    def symlink_to(
        self, target: Union[str, Path], target_is_directory: bool = False
    ) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.symlink_to.__qualname__
        )
        raise NotImplementedError(message)
