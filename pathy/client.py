from dataclasses import dataclass
from typing import Generator, Generic, List, Optional, TypeVar

import smart_open

from .base import PureGCSPath

__all__ = (
    "BucketStat",
    "BucketEntry",
    "BucketClient",
    "ClientError",
    "ClientBucket",
    "ClientBlob",
)

BucketType = TypeVar("BucketType")
BucketBlobType = TypeVar("BucketBlobType")

_SUBCLASS_MUST_IMPLEMENT = "must be implemented in a subclass"


@dataclass
class ClientError(BaseException):
    message: str
    code: int

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"({self.code}) {self.message}"


@dataclass
class BucketStat:
    """Stat for a bucket item"""

    size: int
    last_modified: int


@dataclass
class ClientBlob(Generic[BucketType, BucketBlobType]):
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


class BucketEntry(Generic[BucketType, BucketBlobType]):
    """A single item returned from scanning a path"""

    name: str
    _is_dir: bool
    _stat: BucketStat
    raw: Optional[ClientBlob[BucketType, BucketBlobType]]

    def __init__(
        self,
        name: str,
        is_dir: bool,
        size: int = None,
        last_modified: int = None,
        raw: Optional[ClientBlob[BucketType, BucketBlobType]] = None,
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


class BucketClient:
    """Base class for a client that interacts with a bucket-based storage system."""

    def make_uri(self, path: PureGCSPath) -> str:
        return path.as_uri()

    def is_dir(self, path: PureGCSPath) -> bool:
        return any(self.list_blobs(path, prefix=path.prefix))

    def rmdir(self, path: PureGCSPath) -> None:
        return None

    def exists(self, path: PureGCSPath) -> bool:
        # Because we want all the parents of a valid blob (e.g. "directory" in
        # "directory/foo.file") to return True, we enumerate the blobs with a prefix
        # and compare the object names to see if they match a substring of the path
        key_name = str(path.key)
        for obj in self.list_blobs(path):
            if obj.name == key_name:
                return True
            if obj.name.startswith(key_name + path._flavour.sep):
                return True
        return False

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
            # Disable de/compression based on the file extension
            ignore_ext=True,
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
    ) -> Generator[BucketEntry[BucketType, BucketBlobType], None, None]:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)

    def delete_bucket(self, path: PureGCSPath) -> None:
        raise NotImplementedError(_SUBCLASS_MUST_IMPLEMENT)
