from dataclasses import dataclass
from io import DEFAULT_BUFFER_SIZE
from typing import Generator, Generic, List, Optional, TypeVar

import smart_open

from .base import PurePathy, StreamableType

__all__ = (
    "BlobStat",
    "BucketEntry",
    "BucketClient",
    "ClientError",
    "Bucket",
    "Blob",
)

BucketType = TypeVar("BucketType")
BucketBlobType = TypeVar("BucketBlobType")

_SUBCLASS_MUST_IMPLEMENT = "must be implemented in a subclass"


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

    size: int
    last_modified: int


@dataclass
class Blob(Generic[BucketType, BucketBlobType]):
    bucket: "Bucket"
    name: str
    size: int
    updated: int
    owner: Optional[str]
    raw: BucketBlobType

    def delete(self):
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def exists(self) -> bool:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)


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
        self._stat = BlobStat(size=size, last_modified=last_modified)

    def __repr__(self):
        return "{}(name={}, is_dir={}, stat={})".format(
            type(self).__name__, self.name, self._is_dir, self._stat
        )

    def inode(self, *args, **kwargs):
        return None

    def is_dir(self):
        return self._is_dir

    def is_file(self):
        return not self._is_dir

    def is_symlink(self, *args, **kwargs):
        return False

    def stat(self):
        return self._stat


@dataclass
class Bucket:
    def get_blob(self, blob_name: str) -> Optional[Blob]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def copy_blob(self, blob: Blob, target: "Bucket", name: str) -> Optional[Blob]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_blob(self, blob: Blob) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_blobs(self, blobs: List[Blob]) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def exists(self) -> bool:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)


class BucketClient:
    """Base class for a client that interacts with a bucket-based storage system."""

    def open(
        self,
        path: PurePathy,
        *,
        mode: str = "r",
        buffering: int = DEFAULT_BUFFER_SIZE,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        return smart_open.open(
            self.make_uri(path),
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            # Disable de/compression based on the file extension
            ignore_ext=True,
        )  # type:ignore

    def make_uri(self, path: PurePathy) -> str:
        return path.as_uri()

    def is_dir(self, path: PurePathy) -> bool:
        return any(self.list_blobs(path, prefix=path.prefix))

    def rmdir(self, path: PurePathy) -> None:
        return None

    def exists(self, path: PurePathy) -> bool:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def lookup_bucket(self, path: PurePathy) -> Optional[Bucket]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def get_bucket(self, path: PurePathy) -> Bucket:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def list_buckets(self) -> Generator[Bucket, None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def list_blobs(
        self,
        path: PurePathy,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[Blob, None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def scandir(
        self,
        path: PurePathy = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> Generator[BucketEntry[BucketType, BucketBlobType], None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def create_bucket(self, path: PurePathy) -> Bucket:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_bucket(self, path: PurePathy) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)
