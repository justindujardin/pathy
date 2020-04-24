from dataclasses import dataclass, field
from typing import Optional, List, Generator
from .client import BucketClient, ClientBucket, ClientBlob, ClientError, BucketEntry
from .base import PureGCSPath

try:
    from google.cloud import storage
    from google.api_core import exceptions as gcs_errors

    has_gcs = True
except ImportError:
    storage = None
    has_gcs = False


class BucketEntryGCS(BucketEntry["ClientBucketGCS", storage.Blob]):
    ...


@dataclass
class ClientBlobGCS(ClientBlob["ClientBucketGCS", storage.Blob]):
    def delete(self) -> None:
        self.raw.delete()

    def exists(self) -> bool:
        return self.raw.exists()


@dataclass
class ClientBucketGCS(ClientBucket):
    name: str
    bucket: storage.Bucket

    def get_blob(self, blob_name: str) -> Optional[ClientBlobGCS]:
        native_blob = self.bucket.get_blob(blob_name)
        if native_blob is None:
            return None
        return ClientBlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,
            name=native_blob.name,
            raw=native_blob,
            size=native_blob.size,
            updated=native_blob.updated.timestamp(),
        )

    def copy_blob(
        self, blob: ClientBlobGCS, target: "ClientBucketGCS", name: str
    ) -> Optional[ClientBlobGCS]:
        assert blob.raw is not None, "raw storage.Blob instance required"
        native_blob = self.bucket.copy_blob(blob.raw, target.bucket, name)
        if native_blob is None:
            return None
        return ClientBlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,
            name=native_blob.name,
            raw=native_blob,
            size=native_blob.size,
            updated=native_blob.updated.timestamp(),
        )

    def delete_blob(self, blob: ClientBlobGCS) -> None:
        return self.bucket.delete_blob(blob.name)

    def delete_blobs(self, blobs: List[ClientBlobGCS]) -> None:
        return self.bucket.delete_blobs(blobs)


@dataclass
class BucketClientGCS(BucketClient):
    client: storage.Client = field(default_factory=lambda: storage.Client())

    def make_uri(self, path: PureGCSPath):
        return str(path)

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        return self.client.create_bucket(path.root)

    def delete_bucket(self, path: PureGCSPath) -> None:
        bucket = self.client.get_bucket(path.root)
        bucket.delete()

    def lookup_bucket(self, path: PureGCSPath) -> Optional[ClientBucketGCS]:
        try:
            native_bucket = self.client.lookup_bucket(path.root)
            if native_bucket is not None:
                return ClientBucketGCS(str(path.root), bucket=native_bucket)
        except gcs_errors.ClientError:
            pass
        return None

    def get_bucket(self, path: PureGCSPath) -> ClientBucketGCS:
        try:
            native_bucket = self.client.lookup_bucket(path.root)
            if native_bucket is not None:
                return ClientBucketGCS(str(path.root), bucket=native_bucket)
            raise FileNotFoundError(f"Bucket {path.root} does not exist!")
        except gcs_errors.ClientError as e:
            raise ClientError(message=e.message, code=e.code)

    def list_buckets(self, **kwargs) -> Generator[ClientBucket, None, None]:
        return self.client.list_buckets(**kwargs)

    def scandir(
        self,
        path: Optional[PureGCSPath] = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_raw: bool = False,
    ) -> Generator[BucketEntryGCS, None, None]:
        continuation_token = None
        if path is None or not path.root:
            for bucket in self.list_buckets():
                yield BucketEntryGCS(bucket.name, is_dir=True, raw=None)
            return
        sep = path._flavour.sep
        bucket = self.lookup_bucket(path)
        if bucket is None:
            return
        while True:
            if continuation_token:
                response = self.client.list_blobs(
                    bucket.name,
                    prefix=prefix,
                    delimiter=sep,
                    page_token=continuation_token,
                )
            else:
                response = self.client.list_blobs(
                    bucket.name, prefix=prefix, delimiter=sep
                )
            for page in response.pages:
                for folder in list(page.prefixes):
                    full_name = folder[:-1] if folder.endswith(sep) else folder
                    name = full_name.split(sep)[-1]
                    if name:
                        yield BucketEntryGCS(name, is_dir=True, raw=None)
                for item in page:
                    name = item.name.split(sep)[-1]
                    if name:
                        yield BucketEntryGCS(
                            name=name,
                            is_dir=False,
                            size=item.size,
                            last_modified=item.updated.timestamp(),
                            raw=item,
                        )
            if response.next_page_token is None:
                break
            continuation_token = response.next_page_token

    def list_blobs(
        self,
        path: PureGCSPath,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[ClientBlobGCS, None, None]:
        continuation_token = None
        bucket = self.lookup_bucket(path)
        if bucket is None:
            return
        while True:
            if continuation_token:
                response = self.client.list_blobs(
                    path.root,
                    prefix=prefix,
                    delimiter=delimiter,
                    page_token=continuation_token,
                )
            else:
                response = self.client.list_blobs(
                    path.root, prefix=prefix, delimiter=delimiter
                )
            for page in response.pages:
                for item in page:
                    yield ClientBlobGCS(
                        bucket=bucket,
                        owner=item.owner,
                        name=item.name,
                        raw=item,
                        size=item.size,
                        updated=item.updated.timestamp(),
                    )
            if response.next_page_token is None:
                break
            continuation_token = response.next_page_token
