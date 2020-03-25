from dataclasses import dataclass
from typing import Dict, List, Optional


__all__ = (
    "BucketStatResult",
    "BucketDirEntry",
    "BucketClient",
    "ClientBucket",
    "ClientBlob",
)


@dataclass
class BucketStatResult:
    """Stat for a bucket item"""

    size: Optional[int]
    last_modified: Optional[int]


class BucketDirEntry:
    """A single item returned from scanning a path"""

    name: str
    _is_dir: bool
    _stat: BucketStatResult

    def __init__(
        self, name: str, is_dir: bool, size: int = None, last_modified: int = None
    ):
        self.name = name
        self._is_dir = is_dir
        self._stat = BucketStatResult(size=size, last_modified=last_modified)

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
class ClientBlob:
    bucket: "ClientBucket"
    name: str

    def delete(self):
        pass


@dataclass
class ClientBucket:
    name: str

    def get_blob(self, blob_name: str) -> Optional[ClientBlob]:
        pass


class BucketClient:

    buckets: Dict[str, str]

    def __init__(self):
        self.buckets = {}

    def register_bucket(self, alias: str, bucket_uri: str):
        if alias in self.buckets:
            raise ValueError("alias already exists")
        self.buckets[str(alias)] = str(bucket_uri)

    def lookup_bucket(self, bucket_name: Optional[str]) -> Optional[ClientBucket]:
        raise NotImplementedError("must be implemented in subclass")

    def get_bucket(self, bucket_name: Optional[str]):
        raise NotImplementedError("must be implemented in subclass")

    def list_buckets(self) -> List[ClientBucket]:
        raise NotImplementedError("must be implemented in subclass")

    def list_blobs(
        self,
        bucket_name: Optional[str],
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> List[ClientBlob]:
        raise NotImplementedError("must be implemented in subclass")

    def create_bucket(self, bucket_name: Optional[str]) -> ClientBucket:
        raise NotImplementedError("must be implemented in subclass")
