from typing import cast
import os
import shutil
import tempfile
from collections import namedtuple
from contextlib import suppress
from io import DEFAULT_BUFFER_SIZE
from pathlib import Path, PurePath, _Accessor, _PosixFlavour  # type:ignore
from typing import Generator, Iterable, List, Optional, Union

from google.api_core import exceptions as gcs_errors
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage

from . import gcs
from .base import PureGCSPath, PathType
from .client import (
    BucketClient,
    BucketEntry,
    BucketStat,
    ClientBlob,
    ClientBucket,
    ClientError,
)
from .file import BucketClientFS

__all__ = ("Pathy", "use_fs", "get_fs_client", "BucketsAccessor")

_SUPPORTED_OPEN_MODES = {"r", "rb", "tr", "rt", "w", "wb", "bw", "wt", "tw"}


_fs_client: Optional[BucketClientFS] = None
_fs_cache: Optional[Path] = None


def use_fs(root: Optional[Union[str, Path, bool]] = None) -> Optional[BucketClientFS]:
    """Use a path in the local file-system to store blobs and buckets.

    This is useful for development and testing situations, and for embedded
    applications."""
    global _fs_client
    # False - disable adapter
    if root is False:
        _fs_client = None
        return None

    # None or True - enable FS adapter with default root
    if root is None or root is True:
        # Look up "data" folder of pathy package similar to spaCy
        client_root = Path(__file__).parent / "data"
    else:
        assert isinstance(root, (str, Path)), f"root is not a known type: {type(root)}"
        client_root = Path(root)
    if not client_root.exists():
        client_root.mkdir(parents=True)
    _fs_client = BucketClientFS(root=client_root)
    return _fs_client


def get_fs_client() -> Optional[BucketClientFS]:
    """Get the file-system client (or None)"""
    global _fs_client
    assert _fs_client is None or isinstance(
        _fs_client, BucketClientFS
    ), "invalid root type"
    return _fs_client


def use_fs_cache(root: Optional[Union[str, Path, bool]] = None) -> Optional[Path]:
    """Use a path in the local file-system to cache blobs and buckets.

    This is useful for when you want to avoid fetching large blobs multiple
    times, or need to pass a local file path to a third-party library."""
    global _fs_cache
    # False - disable adapter
    if root is False:
        _fs_cache = None
        return None

    # None or True - enable FS cache with default root
    if root is None or root is True:
        # Use a temporary folder. Cache will be removed according to OS policy
        cache_root = Path(tempfile.mkdtemp())
    else:
        assert isinstance(root, (str, Path)), f"root is not a known type: {type(root)}"
        cache_root = Path(root)
    if not cache_root.exists():
        cache_root.mkdir(parents=True)
    _fs_cache = cache_root
    return cache_root


def get_fs_cache() -> Optional[Path]:
    """Get the file-system client (or None)"""
    global _fs_cache
    assert _fs_cache is None or isinstance(_fs_cache, Path), "invalid root type"
    return _fs_cache


def clear_fs_cache(force: bool = False) -> None:
    """Remove the existing file-system blob cache folder.
    
    Raises AssertionError if the cache path is unset or points to the
    root of the file-system."""
    cache_path = get_fs_cache()
    assert cache_path is not None, "no cache to clear"
    resolved = cache_path.resolve()
    assert str(resolved) != "/", f"refusing to remove a root path: {resolved}"
    shutil.rmtree(str(resolved))


FluidPath = Union["Pathy", Path]


class Pathy(Path, PureGCSPath):
    """Path subclass for GCS service.

    Write files to and read files from the GCS service using pathlib.Path
    methods."""

    __slots__ = ()
    _NOT_SUPPORTED_MESSAGE = "{method} is an unsupported bucket operation"

    def __truediv__(self: PathType, key: Union[str, PathType]) -> PathType:
        return super().__truediv__(key)

    def __rtruediv__(self: PathType, key: Union[str, PathType]) -> PathType:
        return cast(Pathy, super().__rtruediv__(key))

    def _init(self: PathType, template=None):
        super()._init(template)  # type:ignore
        if template is None:
            self._accessor = _gcs_accessor
        else:
            self._accessor = template._accessor

    @classmethod
    def fluid(cls: PathType, path_candidate: Union[str, FluidPath]) -> FluidPath:
        """Helper to infer a pathlib.Path or Pathy from an input path or string.
        
        The returned type is a union of the potential `FluidPath` types and will
        type-check correctly against the minimum overlapping APIs of all the input
        types.
        
        If you need to use specific implementation details of a type, you 
        will need to cast the return of this function to the desired type, e.g.

            # Narrow the type a specific class
            assert isinstance(path, Pathy), "must be Pathy"
            # Use a member specific to that class
            print(path.prefix)

        """
        from_path: FluidPath = Pathy(path_candidate)
        if from_path.root in ["/", ""]:
            from_path = Path(path_candidate)
        return from_path

    @classmethod
    def from_bucket(cls: PathType, bucket_name: str) -> "Pathy":
        """Helper to convert a bucket name into a Pathy without needing
        to add the leading and trailing slashes"""
        return Pathy(f"gs://{bucket_name}/")

    @classmethod
    def to_local(
        cls: PathType, blob_path: Union["Pathy", str], recurse: bool = True
    ) -> Path:
        """Get a bucket blob and return a local file cached version of it. The cache
        is sensitive to the file updated time, and downloads new blobs as they become
        available."""
        cache_folder = get_fs_cache()
        if cache_folder is None:
            raise ValueError(
                'cannot get and cache a blob without first calling "use_fs_cache"'
            )

        cache_folder.mkdir(exist_ok=True, parents=True)
        if isinstance(blob_path, str):
            blob_path = Pathy(blob_path)

        cache_blob: Path = cache_folder.absolute() / blob_path.root / blob_path.key
        cache_time: Path = (
            cache_folder.absolute() / blob_path.root / f"{blob_path.key}.time"
        )
        # Keep a cache of downloaded files. Fetch new ones when:
        #  - the file isn't in the cache
        #  - cached_stat.updated != latest_stat.updated
        if cache_blob.exists() and cache_time.exists():
            fs_time: str = cache_time.read_text()
            gcs_stat: BucketStat = blob_path.stat()
            # If the times match, return the cached blob
            if fs_time == str(gcs_stat.last_modified):
                return cache_blob
            # remove the cache files because they're out of date
            cache_blob.unlink()
            cache_time.unlink()

        # If the file isn't in the cache, download it
        if not cache_blob.exists():
            # Is a blob
            if blob_path.is_file():
                dest_folder = cache_blob.parent
                dest_folder.mkdir(exist_ok=True, parents=True)
                cache_blob.write_bytes(blob_path.read_bytes())
                blob_stat: BucketStat = blob_path.stat()
                cache_time.write_text(str(blob_stat.last_modified))
            elif recurse:
                # If not a specific blob, enumerate all the blobs under
                # the path and cache them, then return the cache folder
                for blob in blob_path.rglob("*"):
                    Pathy.to_local(blob, recurse=False)
        return cache_blob

    def stat(self: PathType) -> BucketStat:
        """
        Returns information about this path.
        The result is looked up at each call to this method
        """
        self._absolute_path_validation()
        if not self.key:
            raise ValueError("cannot stat a bucket without a key")
        return cast(BucketStat, super().stat())

    def exists(self: PathType) -> bool:
        """
        Whether the path points to an existing Bucket, key or key prefix.
        """
        self._absolute_path_validation()
        if not self.bucket:
            return True
        return self._accessor.exists(self)

    def is_dir(self: PathType) -> bool:
        """
        Returns True if the path points to a Bucket or a key prefix, False if it 
        points to a full key path. False is returned if the path doesn’t exist.
        Other errors (such as permission errors) are propagated.
        """
        self._absolute_path_validation()
        if self.bucket and not self.key:
            return True
        return self._accessor.is_dir(self)

    def is_file(self: PathType) -> bool:
        """
        Returns True if the path points to a Bucket key, False if it points to
        Bucket or a key prefix. False is returned if the path doesn’t exist.
        Other errors (such as permission errors) are propagated.
        """
        self._absolute_path_validation()
        if not self.bucket or not self.key:
            return False
        try:
            return bool(self.stat())
        except (gcs_errors.ClientError, FileNotFoundError):
            return False

    def iterdir(self: PathType) -> Generator[PathType, None, None]:
        """
        When the path points to a Bucket or a key prefix, yield path objects of
        the directory contents
        """
        self._absolute_path_validation()
        yield from super().iterdir()

    def glob(self: PathType, pattern) -> Generator[PathType, None, None]:
        """
        Glob the given relative pattern in the Bucket / key prefix represented
        by this path, yielding all matching files (of any kind)
        """
        yield from super().glob(pattern)

    def rglob(self: PathType, pattern) -> Generator[PathType, None, None]:
        """
        This is like calling Pathy.glob with "**/" added in front of the given
        relative pattern.
        """
        yield from super().rglob(pattern)

    def open(
        self: PathType,
        mode="r",
        buffering=DEFAULT_BUFFER_SIZE,
        encoding=None,
        errors=None,
        newline=None,
    ):
        """
        Opens the Bucket key pointed to by the path, returns a Key file object
        that you can read/write with.
        """
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

        if self._closed:
            self._raise_closed()
        return self._accessor.open(
            self,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self: PathType) -> Optional[str]:
        """
        Returns the name of the user owning the Bucket or key.
        Similarly to boto3's ObjectSummary owner attribute
        """
        self._absolute_path_validation()
        if not self.is_file():
            raise FileNotFoundError(str(self))
        return self._accessor.owner(self)

    def resolve(self: PathType) -> PathType:
        """
        Return a copy of this path. All paths are absolute in buckets, so no
        transformation is applied.
        """
        self._absolute_path_validation()
        return self._accessor.resolve(self)

    def rename(self: PathType, target: Union[str, PathType]) -> None:
        """
        Renames this file or Bucket / key prefix / key to the given target.
        If target exists and is a file, it will be replaced silently if the user
        has permission. If path is a key prefix, it will replace all the keys with
        the same prefix to the new target prefix. Target can be either a string or
        another Pathy object.
        """
        self._absolute_path_validation()
        self_type = type(self)
        if not isinstance(target, self_type):
            target = self_type(target)
        target._absolute_path_validation()  # type:ignore
        super().rename(target)

    def replace(self: PathType, target: Union[str, PathType]) -> None:
        """
        Renames this Bucket / key prefix / key to the given target.
        If target points to an existing Bucket / key prefix / key, it will be
        unconditionally replaced.
        """
        self.rename(target)

    def rmdir(self: PathType) -> None:
        """
        Removes this Bucket / key prefix. The Bucket / key prefix must be empty
        """
        self._absolute_path_validation()
        if self.is_file():
            raise NotADirectoryError()
        if not self.is_dir():
            raise FileNotFoundError()
        super().rmdir()

    def samefile(self: PathType, other_path: PathType) -> bool:
        """
        Returns whether this path points to the same Bucket key as other_path,
        Which can be either a Path object, or a string
        """
        self._absolute_path_validation()
        if not isinstance(other_path, Path):
            other_path = type(self)(other_path)
        return (
            self.bucket == other_path.bucket and self.key == self.key and self.is_file()
        )

    def touch(self: PathType, mode: int = 0o666, exist_ok: bool = True):
        """
        Creates a key at this given path.

        If the key already exists, the function succeeds if exist_ok is true
        (and its modification time is updated to the current time), otherwise
        FileExistsError is raised.
        """
        if self.exists() and not exist_ok:
            raise FileExistsError()
        self.write_text("")

    def mkdir(
        self: PathType, mode: int = 0o777, parents: bool = False, exist_ok: bool = False
    ) -> None:
        """
        Create a path bucket.
        GCS Service doesn't support folders, therefore the mkdir method will
        only create the current bucket. If the bucket path already exists,
        FileExistsError is raised.

        If exist_ok is false (the default), FileExistsError is raised if the
        target Bucket already exists.

        If exist_ok is true, OSError exceptions will be ignored.

        if parents is false (the default), mkdir will create the bucket only
        if this is a Bucket path.

        if parents is true, mkdir will create the bucket even if the path
        have a Key path.

        mode argument is ignored.
        """
        try:
            if self.bucket is None:
                raise FileNotFoundError("No bucket in {} {}".format(type(self), self))
            # If the whole path is just the bucket, respect the
            if self.key is None and not exist_ok and self.bucket.exists():
                raise FileExistsError("Bucket {} already exists".format(self.bucket))
            return super().mkdir(mode, parents=parents, exist_ok=exist_ok)
        except OSError:
            if not exist_ok:
                raise

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
    def cwd(cls: PathType):
        """
        cwd class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.cwd.__qualname__)
        raise NotImplementedError(message)

    @classmethod
    def home(cls: PathType):
        """
        home class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.home.__qualname__)
        raise NotImplementedError(message)

    def chmod(self: PathType, mode):
        """
        chmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.chmod.__qualname__)
        raise NotImplementedError(message)

    def expanduser(self: PathType):
        """
        expanduser method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.expanduser.__qualname__
        )
        raise NotImplementedError(message)

    def lchmod(self: PathType, mode):
        """
        lchmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lchmod.__qualname__)
        raise NotImplementedError(message)

    def group(self: PathType):
        """
        group method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.group.__qualname__)
        raise NotImplementedError(message)

    def is_block_device(self: PathType):
        """
        is_block_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_block_device.__qualname__
        )
        raise NotImplementedError(message)

    def is_char_device(self: PathType):
        """
        is_char_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_char_device.__qualname__
        )
        raise NotImplementedError(message)

    def lstat(self: PathType):
        """
        lstat method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lstat.__qualname__)
        raise NotImplementedError(message)

    def symlink_to(self: PathType, *args, **kwargs):
        """
        symlink_to method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.symlink_to.__qualname__
        )
        raise NotImplementedError(message)


class BucketsAccessor(_Accessor):
    """Access data from blob buckets"""

    _client: Optional[BucketClient]

    @property
    def client(self) -> BucketClient:
        global _fs_client
        if _fs_client is not None:
            return _fs_client
        assert self._client is not None, "neither GCS or FS clients are enabled"
        return self._client

    def __init__(self, **kwargs) -> None:
        try:
            self._client = gcs.BucketClientGCS()
        except DefaultCredentialsError:
            self._client = None

    def get_blob(self, path: PathType) -> Optional[ClientBlob]:
        """Get the blob associated with a path or return None"""
        if not path.root:
            return None
        bucket = self.client.lookup_bucket(path)
        if bucket is None:
            return None
        key_name = str(path.key)
        return bucket.get_blob(key_name)

    def unlink(self, path: PathType) -> None:
        """Delete a link to a blob in a bucket."""
        bucket = self.client.get_bucket(path)
        blob: Optional[ClientBlob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        blob.delete()

    def stat(self, path: PathType) -> BucketStat:
        bucket = self.client.get_bucket(path)
        blob: Optional[ClientBlob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        return BucketStat(size=blob.size, last_modified=blob.updated)

    def is_dir(self, path: PathType) -> bool:
        if str(path) == path.root:
            return True
        if self.get_blob(path) is not None:
            return False
        return self.client.is_dir(path)

    def exists(self, path: PathType) -> bool:
        if not path.root:
            return any(self.client.list_buckets())
        try:
            bucket = self.client.lookup_bucket(path)
        except gcs_errors.ClientError:
            return False
        if not path.key:
            return bucket is not None
        if bucket is None:
            return False
        key_name = str(path.key)
        blob = bucket.get_blob(key_name)
        if blob is not None:
            return blob.exists()
        # Determine if the path exists according to the current adapter
        return self.client.exists(path)

    def scandir(self, path: PathType) -> Generator[BucketEntry, None, None]:
        return self.client.scandir(path, prefix=path.prefix)

    def listdir(self, path: PathType) -> Generator[str, None, None]:
        for entry in self.scandir(path):
            yield entry.name

    def open(
        self: PathType,
        path: PathType,
        *,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
    ):
        return self.client.open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self, path: PathType) -> Optional[str]:
        blob: Optional[ClientBlob] = self.get_blob(path)
        return blob.owner if blob is not None else None

    def resolve(self, path: PathType, strict: bool = False) -> PathType:
        path_parts = str(path).replace(path.drive, "")
        return Pathy(f"{path.drive}{os.path.abspath(path_parts)}")

    def rename(self, path: PathType, target: PathType) -> None:
        bucket: ClientBucket = self.client.get_bucket(path)
        target_bucket: ClientBucket = self.client.get_bucket(target)

        # Single file
        if not self.is_dir(path):
            from_blob: Optional[ClientBlob] = bucket.get_blob(str(path.key))
            if from_blob is None:
                raise FileNotFoundError(f'source file "{path}" does not exist')
            target_bucket.copy_blob(from_blob, target_bucket, str(target.key))
            bucket.delete_blob(from_blob)
            return

        # Folder with objects
        sep = path._flavour.sep
        blobs = list(self.client.list_blobs(path, prefix=path.prefix, delimiter=sep))
        # First rename
        for blob in blobs:
            target_key_name = blob.name.replace(str(path.key), str(target.key))
            target_bucket.copy_blob(blob, target_bucket, target_key_name)
        # Then delete the sources
        for blob in blobs:
            bucket.delete_blob(blob)

    def replace(self, path: PathType, target: PathType) -> None:
        return self.rename(path, target)

    def rmdir(self, path: PathType) -> None:
        key_name = str(path.key) if path.key is not None else None
        bucket = self.client.get_bucket(path)
        blobs = list(self.client.list_blobs(path, prefix=key_name))
        bucket.delete_blobs(blobs)
        if self.client.is_dir(path):
            self.client.rmdir(path)

    def mkdir(self, path: PathType, mode) -> None:
        if not self.client.lookup_bucket(path):
            self.client.create_bucket(path)


_gcs_accessor = BucketsAccessor()
