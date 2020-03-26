from dataclasses import dataclass
from typing import Generator, Generic, List, Optional, TypeVar
from .base import PureGCSPath

__all__ = (
    "BucketStat",
    "BucketEntry",
    "Client",
    "ClientError",
    "ClientBucket",
    "ClientBlob",
)

BucketBlobType = TypeVar("BucketBlobType", bound="ClientBlob")


@dataclass
class ClientError(BaseException):
    message: str
    code: int


@dataclass
class BucketStat:
    """Stat for a bucket item"""

    size: Optional[int]
    last_modified: Optional[int]


class BucketEntry:
    """A single item returned from scanning a path"""

    name: str
    _is_dir: bool
    _stat: BucketStat

    def __init__(
        self, name: str, is_dir: bool, size: int = None, last_modified: int = None,
    ):
        self.name = name
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
class ClientBlob(Generic[BucketBlobType]):
    bucket: "ClientBucket"
    name: str
    raw: BucketBlobType

    def delete(self):
        ...

    def exists(self) -> bool:
        ...


@dataclass
class ClientBucket:
    name: str

    def get_blob(self, blob_name: str) -> Optional[ClientBlob]:
        pass


class Client:
    """Base class for a client that interacts with a bucket-based storage system."""

    def lookup_bucket(self, path: PureGCSPath) -> Optional[ClientBucket]:
        raise NotImplementedError("must be implemented in subclass")

    def get_bucket(self, path: PureGCSPath):
        raise NotImplementedError("must be implemented in subclass")

    def list_buckets(self) -> Generator[ClientBucket, None, None]:
        raise NotImplementedError("must be implemented in subclass")

    def list_blobs(
        self,
        path: PureGCSPath,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[ClientBlob, None, None]:
        raise NotImplementedError("must be implemented in subclass")

    def scandir(
        self,
        path: PureGCSPath = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> Generator[BucketEntry, None, None]:
        raise NotImplementedError("must be implemented in subclass")

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        raise NotImplementedError("must be implemented in subclass")
