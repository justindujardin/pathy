import os
from dataclasses import dataclass
from io import DEFAULT_BUFFER_SIZE
from pathlib import _Accessor  # type:ignore
from pathlib import _PosixFlavour  # type:ignore
from pathlib import _WindowsFlavour  # type:ignore
from pathlib import Path, PurePath
from typing import (
    IO,
    Any,
    ContextManager,
    Dict,
    Generator,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import smart_open

SUBCLASS_ERROR = "must be implemented in a subclass"

StreamableType = IO[Any]
FluidPath = Union["Pathy", "BasePath"]
BucketClientType = TypeVar("BucketClientType", bound="BucketClient")
BucketType = TypeVar("BucketType")
BucketBlobType = TypeVar("BucketBlobType")

_windows_flavour = _WindowsFlavour()
_posix_flavour = _PosixFlavour()


@dataclass
class ClientError(BaseException):
    message: str
    code: Optional[int]

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"({self.code}) {self.message}"


@dataclass
class BlobStat:
    """Stat for a bucket item"""

    name: str
    size: Optional[int]
    last_modified: Optional[int]


@dataclass
class Blob(Generic[BucketType, BucketBlobType]):
    bucket: "Bucket"
    name: str
    size: Optional[int]
    updated: Optional[int]
    owner: Optional[str]
    raw: BucketBlobType

    def delete(self) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)

    def exists(self) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)


class BucketEntry(Generic[BucketType, BucketBlobType]):
    """A single item returned from scanning a path"""

    name: str
    _is_dir: bool
    _stat: BlobStat
    raw: Optional[Blob[BucketType, BucketBlobType]]

    def __init__(
        self,
        name: str,
        is_dir: bool = False,
        size: int = -1,
        last_modified: int = -1,
        raw: Optional[Blob[BucketType, BucketBlobType]] = None,
    ):
        self.name = name
        self.raw = raw
        self._is_dir = is_dir
        self._stat = BlobStat(name=name, size=size, last_modified=last_modified)

    def __repr__(self) -> str:
        return "{}(name={}, is_dir={}, stat={})".format(
            type(self).__name__, self.name, self._is_dir, self._stat
        )

    def inode(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        return None

    def is_dir(self) -> bool:
        return self._is_dir

    def is_file(self) -> bool:
        return not self._is_dir

    def is_symlink(self) -> bool:
        return False

    def stat(self) -> BlobStat:
        return self._stat


@dataclass
class Bucket:
    def get_blob(self, blob_name: str) -> Optional[Blob[BucketType, BucketBlobType]]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def copy_blob(
        self, blob: Blob[BucketType, BucketBlobType], target: "Bucket", name: str
    ) -> Optional[Blob[BucketType, BucketBlobType]]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def delete_blob(self, blob: Blob[BucketType, BucketBlobType]) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)

    def delete_blobs(self, blobs: List[Blob[BucketType, BucketBlobType]]) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)

    def exists(self) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)


class BucketClient:
    """Base class for a client that interacts with a bucket-based storage system."""

    def recreate(self, **kwargs: Any) -> None:
        """Recreate any underlying bucket client adapter with the given kwargs"""

    def open(
        self,
        path: "Pathy",
        *,
        mode: str = "r",
        buffering: int = DEFAULT_BUFFER_SIZE,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        client_params = {}
        if hasattr(self, "client_params"):
            client_params = getattr(self, "client_params")

        return smart_open.open(
            self.make_uri(path),
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            transport_params=client_params,
            # Disable de/compression based on the file extension
            ignore_ext=True,
        )  # type:ignore

    def make_uri(self, path: "Pathy") -> str:
        return path.as_uri()

    def is_dir(self, path: "Pathy") -> bool:
        return any(self.list_blobs(path, prefix=path.prefix))

    def rmdir(self, path: "Pathy") -> None:
        return None

    def exists(self, path: "Pathy") -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def lookup_bucket(self, path: "Pathy") -> Optional[Bucket]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def get_bucket(self, path: "Pathy") -> Bucket:
        raise NotImplementedError(SUBCLASS_ERROR)

    def list_buckets(self) -> Generator[Bucket, None, None]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def list_blobs(
        self,
        path: "Pathy",
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[Blob, None, None]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def scandir(
        self,
        path: "Pathy" = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> "PathyScanDir":
        raise NotImplementedError(SUBCLASS_ERROR)

    def create_bucket(self, path: "Pathy") -> Bucket:
        raise NotImplementedError(SUBCLASS_ERROR)

    def delete_bucket(self, path: "Pathy") -> None:
        raise NotImplementedError(SUBCLASS_ERROR)


class _PathyFlavour(_PosixFlavour):
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

    def make_uri(self, path: "Pathy") -> str:
        uri = super().make_uri(path)
        return uri.replace("file:///", "gs://")


class PurePathy(PurePath):
    """PurePath subclass for bucket storage."""

    _flavour = _PathyFlavour()
    __slots__ = ()

    @property
    def scheme(self) -> str:
        """Return the scheme portion of this path. A path's scheme is the leading
        few characters. In a website you would see a scheme of "http" or "https".

        Consider a few examples:

        ```python
        assert Pathy("gs://foo/bar").scheme == "gs"
        assert Pathy("file:///tmp/foo/bar").scheme == "file"
        assert Pathy("/dev/null").scheme == ""

        """
        # If there is no drive, return nothing
        if self.drive == "":
            return ""
        # This is an assumption of mine. I think it's fine, but let's
        # cause an error if it's not the case.
        assert self.drive[-1] == ":", "drive should end with :"
        return self.drive[:-1]

    @property
    def bucket(self) -> "Pathy":
        """Return a new instance of only the bucket path."""
        self._absolute_path_validation()
        return cast(Pathy, type(self)(f"{self.drive}//{self.root}"))

    @property
    def key(self) -> Optional["Pathy"]:
        """Return a new instance of only the key path."""
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key or len(self.parts) < 2:
            return None
        return cast(Pathy, type(self)(key))

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


_SUPPORTED_OPEN_MODES = {"r", "rb", "tr", "rt", "w", "wb", "bw", "wt", "tw"}


class _PathyExtensions:
    def ls(self) -> Generator["BlobStat", None, None]:
        blobs: "PathyScanDir" = self._accessor.scandir(self)  # type:ignore
        for blob in blobs:
            if hasattr(blob, "_stat"):
                yield blob._stat
            elif isinstance(blob, os.DirEntry):
                os_blob = cast(os.DirEntry, blob)
                stat = os_blob.stat()
                file_size = stat.st_size
                updated = int(round(stat.st_mtime))
                yield BlobStat(name=os_blob.name, size=file_size, last_modified=updated)


class BasePath(_PathyExtensions, Path):
    # NOTE: pathlib normally takes care of this, but the logic checks
    #       for specifically "Path" type class in __new__ so we need to
    #       set the flavour manually based on the OS.
    _flavour = _windows_flavour if os.name == "nt" else _posix_flavour  # type:ignore


class BucketsAccessor(_Accessor):
    """Access data from blob buckets"""

    _client: Optional[BucketClient]

    def client(self, path: "Pathy") -> BucketClient:
        # lazily avoid circular imports
        from .clients import get_client

        return get_client(path.scheme)

    def get_blob(self, path: "Pathy") -> Optional[Blob]:
        """Get the blob associated with a path or return None"""
        if not path.root:
            return None
        bucket = self.client(path).lookup_bucket(path)
        if bucket is None:
            return None
        key_name = str(path.key)
        return bucket.get_blob(key_name)

    def unlink(self, path: "Pathy") -> None:
        """Delete a link to a blob in a bucket."""
        bucket = self.client(path).get_bucket(path)
        blob: Optional[Blob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        blob.delete()

    def stat(self, path: "Pathy") -> BlobStat:
        bucket = self.client(path).get_bucket(path)
        blob: Optional[Blob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        return BlobStat(name=str(blob), size=blob.size, last_modified=blob.updated)

    def is_dir(self, path: "Pathy") -> bool:
        if str(path) == path.root:
            return True
        if self.get_blob(path) is not None:
            return False
        return self.client(path).is_dir(path)

    def exists(self, path: "Pathy") -> bool:
        client = self.client(path)
        if not path.root:
            return any(client.list_buckets())
        try:
            bucket = client.lookup_bucket(path)
        except ClientError:
            return False
        if bucket is None or not bucket.exists():
            return False
        if not path.key:
            return True

        key_name = str(path.key)
        blob: Optional[Blob] = bucket.get_blob(key_name)
        if blob is not None:
            return blob.exists()
        # Determine if the path exists according to the current adapter
        return client.exists(path)

    def scandir(self, path: "Pathy") -> "PathyScanDir":
        return self.client(path).scandir(path, prefix=path.prefix)

    def listdir(self, path: "Pathy") -> Generator[str, None, None]:
        with self.scandir(path) as entries:
            for entry in entries:
                yield entry.name

    def open(
        self,
        path: "Pathy",
        *,
        mode: str = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        return self.client(path).open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self, path: "Pathy") -> Optional[str]:
        blob: Optional[Blob] = self.get_blob(path)
        return blob.owner if blob is not None else None

    def resolve(self, path: "Pathy", strict: bool = False) -> "Pathy":
        path_parts = str(path).replace(path.drive, "")
        return Pathy(f"{path.drive}{os.path.abspath(path_parts)}")

    def rename(self, path: "Pathy", target: "Pathy") -> None:
        client: BucketClient = self.client(path)
        bucket: Bucket = client.get_bucket(path)
        target_bucket: Bucket = client.get_bucket(target)

        # Single file
        if not self.is_dir(path):
            from_blob: Optional[Blob] = bucket.get_blob(str(path.key))
            if from_blob is None:
                raise FileNotFoundError(f'source file "{path}" does not exist')
            target_bucket.copy_blob(from_blob, target_bucket, str(target.key))
            bucket.delete_blob(from_blob)
            return

        # Folder with objects
        sep = path._flavour.sep
        blobs = list(client.list_blobs(path, prefix=path.prefix, delimiter=sep))
        # First rename
        for blob in blobs:
            target_key_name = blob.name.replace(str(path.key), str(target.key))
            target_bucket.copy_blob(blob, target_bucket, target_key_name)
        # Then delete the sources
        for blob in blobs:
            bucket.delete_blob(blob)

    def replace(self, path: "Pathy", target: "Pathy") -> None:
        return self.rename(path, target)

    def rmdir(self, path: "Pathy") -> None:
        client: BucketClient = self.client(path)
        key_name = str(path.key) if path.key is not None else None
        bucket: Bucket = client.get_bucket(path)
        blobs = list(client.list_blobs(path, prefix=key_name))
        bucket.delete_blobs(blobs)
        # The path is just the bucket
        if key_name is None:
            client.delete_bucket(path)
        elif client.is_dir(path):
            client.rmdir(path)

    def mkdir(self, path: "Pathy", mode: int) -> None:
        client: BucketClient = self.client(path)
        bucket: Optional[Bucket] = client.lookup_bucket(path)
        if bucket is None or not bucket.exists():
            client.create_bucket(path)
        elif isinstance(path, Pathy) and path.key is not None:
            assert isinstance(path, Pathy)
            blob: Optional[Blob] = bucket.get_blob(str(path.key))
            if blob is not None and blob.exists():
                raise OSError(f"Blob already exists: {path}")


class Pathy(Path, PurePathy, _PathyExtensions):
    """Subclass of `pathlib.Path` that works with bucket APIs."""

    __slots__ = ()
    _accessor: "BucketsAccessor"
    _default_accessor = BucketsAccessor()
    _NOT_SUPPORTED_MESSAGE = "{method} is an unsupported bucket operation"

    def __truediv__(self, key: Union[str, Path, "Pathy", PurePathy]) -> "Pathy":  # type: ignore[override]
        return super().__truediv__(key)  # type:ignore

    def __rtruediv__(self, key: Union[str, Path, "Pathy", PurePathy]) -> "Pathy":  # type: ignore[override]
        return super().__rtruediv__(key)  # type:ignore

    def _init(self: "Pathy", template: Optional[Any] = None) -> None:
        super()._init(template)  # type:ignore
        if template is None:
            self._accessor = Pathy._default_accessor
        else:
            self._accessor = template._accessor

    @classmethod
    def fluid(cls, path_candidate: Union[str, FluidPath]) -> FluidPath:
        """Infer either a Pathy or pathlib.Path from an input path or string.

        The returned type is a union of the potential `FluidPath` types and will
        type-check correctly against the minimum overlapping APIs of all the input
        types.

        If you need to use specific implementation details of a type, "narrow" the
        return of this function to the desired type, e.g.

        ```python
        from pathy import FluidPath, Pathy

        fluid_path: FluidPath = Pathy.fluid("gs://my_bucket/foo.txt")
        # Narrow the type to a specific class
        assert isinstance(fluid_path, Pathy), "must be Pathy"
        # Use a member specific to that class
        assert fluid_path.prefix == "foo.txt/"
        ```
        """
        from_path: FluidPath = Pathy(path_candidate)
        if from_path.root in ["/", ""]:
            from_path = BasePath(path_candidate)
        return from_path

    @classmethod
    def from_bucket(cls, bucket_name: str) -> "Pathy":
        """Initialize a Pathy from a bucket name. This helper adds a trailing slash and
        the appropriate prefix.

        ```python
        from pathy import Pathy

        assert str(Pathy.from_bucket("one")) == "gs://one/"
        assert str(Pathy.from_bucket("two")) == "gs://two/"
        ```
        """
        return Pathy(f"gs://{bucket_name}/")  # type:ignore

    @classmethod
    def to_local(cls, blob_path: Union["Pathy", str], recurse: bool = True) -> Path:
        """Download and cache either a blob or a set of blobs matching a prefix.

        The cache is sensitive to the file updated time, and downloads new blobs
        as their updated timestamps change."""
        from .clients import get_fs_cache

        cache_folder = get_fs_cache()
        if cache_folder is None:
            raise ValueError(
                'cannot get and cache a blob without first calling "use_fs_cache"'
            )

        cache_folder.mkdir(exist_ok=True, parents=True)

        in_path: Pathy
        if not isinstance(blob_path, Pathy):
            in_path = Pathy(blob_path)
        else:
            in_path = blob_path

        cache_blob: Path = cache_folder.absolute() / in_path.root
        if in_path.key is not None:
            cache_blob /= in_path.key
        cache_time: Path = (
            cache_folder.absolute() / in_path.root / f"{in_path.key}.time"
        )
        # Keep a cache of downloaded files. Fetch new ones when:
        #  - the file isn't in the cache
        #  - cached_stat.updated != latest_stat.updated
        if cache_blob.exists() and cache_time.exists():
            fs_time: str = cache_time.read_text()
            gcs_stat: BlobStat = in_path.stat()
            # If the times match, return the cached blob
            if fs_time == str(gcs_stat.last_modified):
                return cache_blob
            # remove the cache files because they're out of date
            cache_blob.unlink()
            cache_time.unlink()

        # If the file isn't in the cache, download it
        if not cache_blob.exists():
            # Is a blob
            if in_path.is_file():
                dest_folder = cache_blob.parent
                dest_folder.mkdir(exist_ok=True, parents=True)
                cache_blob.write_bytes(in_path.read_bytes())
                blob_stat: BlobStat = in_path.stat()
                cache_time.write_text(str(blob_stat.last_modified))
            elif recurse:
                # If not a specific blob, enumerate all the blobs under
                # the path and cache them, then return the cache folder
                for blob in in_path.rglob("*"):
                    Pathy.to_local(blob, recurse=False)
        return cache_blob

    def ls(self: "Pathy") -> Generator["BlobStat", None, None]:
        """List blob names with stat information under the given path.

        This is considerably faster than using iterdir if you also need
        the stat information for the enumerated blobs.

        Yields BlobStat objects for each found blob.
        """
        yield from super(Pathy, self).ls()

    def stat(self: "Pathy") -> BlobStat:  # type: ignore[override]
        """Returns information about this bucket path."""
        self._absolute_path_validation()
        if not self.key:
            raise ValueError("cannot stat a bucket without a key")
        return cast(BlobStat, super().stat())

    def exists(self) -> bool:
        """Returns True if the path points to an existing bucket, blob, or prefix."""
        self._absolute_path_validation()
        return self._accessor.exists(self)

    def is_dir(self: "Pathy") -> bool:
        """Determine if the path points to a bucket or a prefix of a given blob
        in the bucket.

        Returns True if the path points to a bucket or a blob prefix.
        Returns False if it points to a blob or the path doesn't exist.
        """
        self._absolute_path_validation()
        if self.bucket and not self.key:
            return True
        return self._accessor.is_dir(self)

    def is_file(self: "Pathy") -> bool:
        """Determine if the path points to a blob in the bucket.

        Returns True if the path points to a blob.
        Returns False if it points to a bucket or blob prefix, or if the path doesn’t
        exist.
        """
        self._absolute_path_validation()
        if not self.bucket or not self.key:
            return False
        try:
            return bool(self.stat())
        except (ClientError, FileNotFoundError):
            return False

    def iterdir(self: "Pathy") -> Generator["Pathy", None, None]:
        """Iterate over the blobs found in the given bucket or blob prefix path."""
        self._absolute_path_validation()
        yield from super().iterdir()  # type:ignore

    def glob(self: "Pathy", pattern: str) -> Generator["Pathy", None, None]:
        """Perform a glob match relative to this Pathy instance, yielding all matched
        blobs."""
        yield from super().glob(pattern)  # type:ignore

    def rglob(self: "Pathy", pattern: str) -> Generator["Pathy", None, None]:
        """Perform a recursive glob match relative to this Pathy instance, yielding
        all matched blobs. Imagine adding "**/" before a call to glob."""
        yield from super().rglob(pattern)  # type:ignore

    def open(  # type:ignore
        self: "Pathy",
        mode: str = "r",
        buffering: int = DEFAULT_BUFFER_SIZE,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        """Open the given blob for streaming. This delegates to the `smart_open`
        library that handles large file streaming for a number of bucket API
        providers."""
        self._absolute_path_validation()
        if mode not in _SUPPORTED_OPEN_MODES:
            raise ValueError(
                "supported modes are {} got {}".format(_SUPPORTED_OPEN_MODES, mode)
            )
        if buffering == 0 or buffering == 1:
            raise ValueError(
                "supported buffering values are only block sizes, no 0 or 1"
            )
        if "b" in mode and encoding:
            raise ValueError("binary mode doesn't take an encoding argument")

        # Leftover pathlib internals stuff
        if hasattr(self, "_closed") and self._closed:  # type:ignore
            self._raise_closed()  # type:ignore
        return self._accessor.open(
            self,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self: "Pathy") -> Optional[str]:  # type:ignore[override]
        """Returns the name of the user that owns the bucket or blob
        this path points to. Returns None if the owner is unknown or
        not supported by the bucket API provider."""
        self._absolute_path_validation()
        if not self.is_file():
            raise FileNotFoundError(str(self))
        return self._accessor.owner(self)

    def resolve(self, strict: bool = False) -> "Pathy":
        """Resolve the given path to remove any relative path specifiers.

        ```python
        from pathy import Pathy

        path = Pathy("gs://my_bucket/folder/../blob")
        assert path.resolve() == Pathy("gs://my_bucket/blob")
        ```
        """
        self._absolute_path_validation()
        return self._accessor.resolve(self, strict=strict)

    def rename(self: "Pathy", target: Union[str, PurePath]) -> "Pathy":  # type:ignore
        """Rename this path to the given target.

        If the target exists and is a file, it will be replaced silently if the user
        has permission.

        If path is a blob prefix, it will replace all the blobs with the same prefix
        to match the target prefix."""
        self._absolute_path_validation()
        self_type = type(self)
        result = target if isinstance(target, self_type) else self_type(target)
        result._absolute_path_validation()  # type:ignore
        super().rename(result)
        return result

    def replace(self: "Pathy", target: Union[str, PurePath]) -> "Pathy":  # type:ignore
        """Renames this path to the given target.

        If target points to an existing path, it will be replaced."""
        return self.rename(target)

    def rmdir(self: "Pathy") -> None:
        """Removes this bucket or blob prefix. It must be empty."""
        self._absolute_path_validation()
        if self.is_file():
            raise NotADirectoryError()
        if not self.is_dir():
            raise FileNotFoundError()
        super().rmdir()

    def samefile(self: "Pathy", other_path: Union[str, bytes, int, Path]) -> bool:
        """Determine if this path points to the same location as other_path."""
        self._absolute_path_validation()
        if not isinstance(other_path, Path):
            other_path = type(self)(other_path)  # type:ignore
        assert isinstance(other_path, Pathy)
        return (
            self.bucket == other_path.bucket and self.key == self.key and self.is_file()
        )

    def touch(self: "Pathy", mode: int = 0o666, exist_ok: bool = True) -> None:
        """Create a blob at this path.

        If the blob already exists, the function succeeds if exist_ok is true
        (and its modification time is updated to the current time), otherwise
        FileExistsError is raised.
        """
        if self.exists() and not exist_ok:
            raise FileExistsError()
        self.write_text("")

    def mkdir(
        self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False
    ) -> None:
        """Create a bucket from the given path. Since bucket APIs only have implicit
        folder structures (determined by the existence of a blob with an overlapping
        prefix) this does nothing other than create buckets.

        If parents is False, the bucket will only be created if the path points to
        exactly the bucket and nothing else. If parents is true the bucket will be
        created even if the path points to a specific blob.

        The mode param is ignored.

        Raises FileExistsError if exist_ok is false and the bucket already exists.
        """
        try:
            if self.bucket is None:
                raise FileNotFoundError("No bucket in {} {}".format(type(self), self))
            # If the whole path is just the bucket, respect the result of "bucket.exists()"
            if self.key is None and not exist_ok and self.bucket.exists():
                raise FileExistsError("Bucket {} already exists".format(self.bucket))
            return super().mkdir(mode, parents=parents, exist_ok=exist_ok)
        except OSError:
            if not exist_ok:
                raise

    def is_mount(self: "Pathy") -> bool:
        return False

    def is_symlink(self: "Pathy") -> bool:
        return False

    def is_socket(self: "Pathy") -> bool:
        return False

    def is_fifo(self: "Pathy") -> bool:
        return False

    # Unsupported operations below here

    @classmethod
    def cwd(cls) -> "Pathy":
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.cwd.__qualname__)
        raise NotImplementedError(message)

    @classmethod
    def home(cls) -> "Pathy":
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.home.__qualname__)
        raise NotImplementedError(message)

    def chmod(self: "Pathy", mode: int) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.chmod.__qualname__)
        raise NotImplementedError(message)

    def expanduser(self: "Pathy") -> "Pathy":
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.expanduser.__qualname__
        )
        raise NotImplementedError(message)

    def lchmod(self: "Pathy", mode: int) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lchmod.__qualname__)
        raise NotImplementedError(message)

    def group(self: "Pathy") -> str:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.group.__qualname__)
        raise NotImplementedError(message)

    def is_block_device(self: "Pathy") -> bool:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_block_device.__qualname__
        )
        raise NotImplementedError(message)

    def is_char_device(self: "Pathy") -> bool:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_char_device.__qualname__
        )
        raise NotImplementedError(message)

    def lstat(self: "Pathy") -> os.stat_result:
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lstat.__qualname__)
        raise NotImplementedError(message)

    def symlink_to(
        self, target: Union[str, Path], target_is_directory: bool = False
    ) -> None:
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.symlink_to.__qualname__
        )
        raise NotImplementedError(message)


class PathyScanDir(Iterator[Any], ContextManager[Any]):
    """A scandir implementation that works for all python 3.x versions.

    Python < 3.7 requires that scandir be iterable so it can be converted
    to a list of results.

    Python >= 3.8 requires that scandir work as a context manager.
    """

    def __init__(
        self,
        client: BucketClient,
        path: Optional[PurePathy] = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._client = client
        self._path = path
        self._prefix = prefix
        self._delimiter = delimiter
        self._generator = self.scandir()

    def __enter__(self) -> Generator[BucketEntry, None, None]:
        return self._generator

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        pass

    def __next__(self) -> Generator[BucketEntry, None, None]:
        yield from self._generator

    def __iter__(self) -> Generator[BucketEntry, None, None]:
        yield from self._generator

    def scandir(self) -> Generator[BucketEntry, None, None]:
        raise NotImplementedError("must be implemented in a subclass")
