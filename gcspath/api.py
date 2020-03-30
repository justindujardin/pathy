from collections import namedtuple
from contextlib import suppress
from io import DEFAULT_BUFFER_SIZE
from pathlib import Path, PurePath, _Accessor, _PosixFlavour
from typing import Generator, Iterable, List, Optional, Union

import smart_open
from google.api_core import exceptions as gcs_errors
from google.cloud import storage

from .base import PureGCSPath
from .client import (
    BucketEntry,
    BucketStat,
    BucketClient,
    ClientBlob,
    ClientBucket,
    ClientError,
)
from .gcs import BucketClientGCS, has_gcs
from .file import BucketClientFS

__all__ = ("GCSPath",)

_SUPPORTED_OPEN_MODES = {"r", "rb", "tr", "rt", "w", "wb", "bw", "wt", "tw"}


_fs_client: Optional[BucketClientFS] = None


def use_fs(root: Optional[Union[str, bool]] = None) -> Optional[BucketClientFS]:
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
        # Look up "data" folder of gcspath package similar to spaCy
        client_root = Path(__file__).parent / "data"
    else:
        assert isinstance(root, str), f"root is not a known type: {type(root)}"
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


class BucketsAccessor(_Accessor):
    """Access data from blob buckets"""

    _client: BucketClient

    @property
    def client(self) -> BucketClient:
        global _fs_client
        if _fs_client is not None:
            return _fs_client
        return self._client

    def __init__(self, **kwargs):
        self._client = BucketClientGCS()

    def get_blob(self, path: "GCSPath") -> Optional[ClientBlob]:
        """Get the blob associated with a path or return None"""
        if not path.bucket_name:
            return None
        bucket = self.client.lookup_bucket(path)
        if bucket is None:
            return None
        key_name = str(path.key)
        return bucket.get_blob(key_name)

    def unlink(self, path: "GCSPath"):
        """Delete a link to a blob in a bucket."""
        bucket = self.client.get_bucket(path)
        blob: Optional[ClientBlob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        return blob.delete()

    def stat(self, path: "GCSPath"):
        bucket = self.client.get_bucket(path)
        blob: Optional[ClientBlob] = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        return BucketStat(size=blob.size, last_modified=blob.updated)

    def is_dir(self, path: "GCSPath"):
        if str(path) == path.root:
            return True
        if self.get_blob(path) is not None:
            return False
        return self.client.is_dir(path)

    def exists(self, path: "GCSPath") -> bool:
        if not path.bucket_name:
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

    def scandir(self, path: "GCSPath") -> Generator[BucketEntry, None, None]:
        return self.client.scandir(path, prefix=path.prefix)

    def listdir(self, path: "GCSPath") -> List[str]:
        return [entry.name for entry in self.scandir(path)]

    def open(
        self,
        path: "GCSPath",
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

    def owner(self, path: "GCSPath") -> Optional[str]:
        blob: Optional[ClientBlob] = self.get_blob(path)
        return blob.owner if blob is not None else None

    def rename(self, path: "GCSPath", target: "GCSPath"):
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

    def replace(self, path: "GCSPath", target: "GCSPath"):
        return self.rename(path, target)

    def rmdir(self, path: "GCSPath") -> None:
        key_name = str(path.key) if path.key is not None else None
        bucket = self.client.get_bucket(path)
        blobs = list(self.client.list_blobs(path, prefix=key_name))
        bucket.delete_blobs(blobs)
        if self.client.is_dir(path):
            self.client.rmdir(path)

    def mkdir(self, path: "GCSPath", mode) -> None:
        self.client.create_bucket(path)


class _PathNotSupportedMixin:
    _NOT_SUPPORTED_MESSAGE = "{method} is unsupported on GCS service"

    @classmethod
    def cwd(cls):
        """
        cwd class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.cwd.__qualname__)
        raise NotImplementedError(message)

    @classmethod
    def home(cls):
        """
        home class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.home.__qualname__)
        raise NotImplementedError(message)

    def chmod(self, mode):
        """
        chmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.chmod.__qualname__)
        raise NotImplementedError(message)

    def expanduser(self):
        """
        expanduser method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.expanduser.__qualname__
        )
        raise NotImplementedError(message)

    def lchmod(self, mode):
        """
        lchmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lchmod.__qualname__)
        raise NotImplementedError(message)

    def group(self):
        """
        group method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.group.__qualname__)
        raise NotImplementedError(message)

    def is_block_device(self):
        """
        is_block_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_block_device.__qualname__
        )
        raise NotImplementedError(message)

    def is_char_device(self):
        """
        is_char_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_char_device.__qualname__
        )
        raise NotImplementedError(message)

    def lstat(self):
        """
        lstat method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lstat.__qualname__)
        raise NotImplementedError(message)

    def resolve(self, strict=False):
        """
        resolve method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.resolve.__qualname__)
        raise NotImplementedError(message)

    def symlink_to(self, *args, **kwargs):
        """
        symlink_to method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.symlink_to.__qualname__
        )
        raise NotImplementedError(message)


_gcs_accessor = BucketsAccessor()


class GCSPath(_PathNotSupportedMixin, Path, PureGCSPath):
    """Path subclass for GCS service.

    Write files to and read files from the GCS service using pathlib.Path
    methods."""

    __slots__ = ()

    def _init(self, template=None):
        super()._init(template)
        if template is None:
            self._accessor = _gcs_accessor
        else:
            self._accessor = template._accessor

    def stat(self):
        """
        Returns information about this path.
        The result is looked up at each call to this method
        """
        self._absolute_path_validation()
        if not self.key:
            return None
        return super().stat()

    def exists(self):
        """
        Whether the path points to an existing Bucket, key or key prefix.
        """
        self._absolute_path_validation()
        if not self.bucket:
            return True
        return self._accessor.exists(self)

    def is_dir(self):
        """
        Returns True if the path points to a Bucket or a key prefix, False if it 
        points to a full key path. False is returned if the path doesn’t exist.
        Other errors (such as permission errors) are propagated.
        """
        self._absolute_path_validation()
        if self.bucket and not self.key:
            return True
        return self._accessor.is_dir(self)

    def is_file(self):
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

    def iterdir(self):
        """
        When the path points to a Bucket or a key prefix, yield path objects of
        the directory contents
        """
        self._absolute_path_validation()
        yield from super().iterdir()

    def glob(self, pattern):
        """
        Glob the given relative pattern in the Bucket / key prefix represented
        by this path, yielding all matching files (of any kind)
        """
        yield from super().glob(pattern)

    def rglob(self, pattern):
        """
        This is like calling GCSPath.glob with "**/" added in front of the given
        relative pattern.
        """
        yield from super().rglob(pattern)

    def open(
        self,
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

    def owner(self):
        """
        Returns the name of the user owning the Bucket or key.
        Similarly to boto3's ObjectSummary owner attribute
        """
        self._absolute_path_validation()
        if not self.is_file():
            raise FileNotFoundError(str(self))
        return self._accessor.owner(self)

    def rename(self, target):
        """
        Renames this file or Bucket / key prefix / key to the given target.
        If target exists and is a file, it will be replaced silently if the user
        has permission. If path is a key prefix, it will replace all the keys with
        the same prefix to the new target prefix. Target can be either a string or
        another GCSPath object.
        """
        self._absolute_path_validation()
        if not isinstance(target, type(self)):
            target = type(self)(target)
        target._absolute_path_validation()
        return super().rename(target)

    def replace(self, target):
        """
        Renames this Bucket / key prefix / key to the given target.
        If target points to an existing Bucket / key prefix / key, it will be
        unconditionally replaced.
        """
        return self.rename(target)

    def rmdir(self):
        """
        Removes this Bucket / key prefix. The Bucket / key prefix must be empty
        """
        self._absolute_path_validation()
        if self.is_file():
            raise NotADirectoryError()
        if not self.is_dir():
            raise FileNotFoundError()
        return super().rmdir()

    def samefile(self, other_path):
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

    def touch(self, mode=0o666, exist_ok=True):
        """
        Creates a key at this given path.

        If the key already exists, the function succeeds if exist_ok is true
        (and its modification time is updated to the current time), otherwise
        FileExistsError is raised.
        """
        if self.exists() and not exist_ok:
            raise FileExistsError()
        self.write_text("")

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
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
            if self.key is not None and not parents:
                raise FileNotFoundError(
                    "Only bucket path can be created, got {}".format(self)
                )
            if self.bucket.exists():
                raise FileExistsError("Bucket {} already exists".format(self.bucket))
            return super().mkdir(mode, parents=parents, exist_ok=exist_ok)
        except OSError:
            if not exist_ok:
                raise

    def is_mount(self):
        return False

    def is_symlink(self):
        return False

    def is_socket(self):
        return False

    def is_fifo(self):
        return False
