from dataclasses import dataclass
from typing import Generator, Generic, List, Optional, TypeVar

import smart_open

from .base import PureGCSPath

__all__ = (
    "BucketStat",
    "BucketEntry",
    "Client",
    "ClientError",
    "ClientBucket",
    "ClientBlob",
)

BucketBlobType = TypeVar("BucketBlobType")

_SUBCLASS_MUST_IMPLEMENT = "must be implemented in a subclass"


@dataclass
class ClientError(BaseException):
    message: str
    code: int


@dataclass
class BucketStat:
    """Stat for a bucket item"""

    size: Optional[int]
    last_modified: Optional[int]


@dataclass
class ClientBlob(Generic[BucketBlobType]):
    bucket: "ClientBucket"
    name: str
    size: int
    updated: int
    owner: Optional[str]
    raw: BucketBlobType

    def delete(self):
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def exists(self) -> bool:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)


class BucketEntry(Generic[BucketBlobType]):
    """A single item returned from scanning a path"""

    name: str
    _is_dir: bool
    _stat: BucketStat
    raw: Optional[ClientBlob[BucketBlobType]]

    def __init__(
        self,
        name: str,
        is_dir: bool,
        size: int = None,
        last_modified: int = None,
        raw: Optional[ClientBlob[BucketBlobType]] = None,
    ):
        self.name = name
        self.raw = raw
        self._is_dir = is_dir
        self._stat = BucketStat(size=size, last_modified=last_modified)

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
class ClientBucket:
    def get_blob(self, blob_name: str) -> Optional[ClientBlob]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def copy_blob(
        self, blob: ClientBlob, target: "ClientBucket", name: str
    ) -> Optional[ClientBlob]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_blob(self, blob: ClientBlob) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_blobs(self, blobs: List[ClientBlob]) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)


class Client:
    """Base class for a client that interacts with a bucket-based storage system."""

    def make_uri(self, path: PureGCSPath) -> str:
        return path.as_uri()

    def open(
        self,
        path: PureGCSPath,
        *,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
    ):
        return smart_open.open(
            self.make_uri(path),
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def lookup_bucket(self, path: PureGCSPath) -> Optional[ClientBucket]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def get_bucket(self, path: PureGCSPath) -> ClientBucket:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def list_buckets(self) -> Generator[ClientBucket, None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def list_blobs(
        self,
        path: PureGCSPath,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[ClientBlob, None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def scandir(
        self,
        path: PureGCSPath = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> Generator[BucketEntry[BucketBlobType], None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)
