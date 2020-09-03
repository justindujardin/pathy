from dataclasses import dataclass
from io import DEFAULT_BUFFER_SIZE
from typing import Any, Dict, Generator, Generic, List, Optional, TypeVar

import smart_open

from .base import SUBCLASS_ERROR, BlobStat, PathType, StreamableType

__all__ = (
    "BucketEntry",
    "BucketClient",
    "ClientError",
    "Bucket",
    "Blob",
)

BucketClientType = TypeVar("BucketClientType", bound="BucketClient")
BucketType = TypeVar("BucketType", bound="Bucket")
BucketBlobType = TypeVar("BucketBlobType", bound="Blob")


@dataclass
class ClientError(BaseException):
    message: str
    code: Optional[int]

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"({self.code}) {self.message}"


@dataclass
class Blob(Generic[BucketType, BucketBlobType]):
    bucket: "Bucket"
    name: str
    size: int
    updated: int
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
        self._stat = BlobStat(size=size, last_modified=last_modified)

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

    def open(
        self,
        path: PathType,
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

    def make_uri(self, path: PathType) -> str:
        return path.as_uri()

    def is_dir(self, path: PathType) -> bool:
        return any(self.list_blobs(path, prefix=path.prefix))

    def rmdir(self, path: PathType) -> None:
        return None

    def exists(self, path: PathType) -> bool:
        raise NotImplementedError(SUBCLASS_ERROR)

    def lookup_bucket(self, path: PathType) -> Optional[Bucket]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def get_bucket(self, path: PathType) -> Bucket:
        raise NotImplementedError(SUBCLASS_ERROR)

    def list_buckets(self) -> Generator[Bucket, None, None]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def list_blobs(
        self,
        path: PathType,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[Blob, None, None]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def scandir(
        self,
        path: PathType = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> Generator[BucketEntry[BucketType, BucketBlobType], None, None]:
        raise NotImplementedError(SUBCLASS_ERROR)

    def create_bucket(self, path: PathType) -> Bucket:
        raise NotImplementedError(SUBCLASS_ERROR)

    def delete_bucket(self, path: PathType) -> None:
        raise NotImplementedError(SUBCLASS_ERROR)
