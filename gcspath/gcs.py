from typing import Optional, List, Generator
from .client import Client, ClientBucket, ClientBlob, ClientError, BucketEntry
from .base import PureGCSPath

try:
    from google.cloud import storage
    from google.api_core import exceptions as gcs_errors

    has_gcs = True
except ImportError:
    storage = None
    has_gcs = False


class BucketClientGCS(Client):
    client: storage.Client

    def __init__(self, client: storage.Client = None):
        if client is None:
            client = storage.Client()
        self.client = client

    def lookup_bucket(self, path: PureGCSPath) -> Optional[ClientBucket]:
        try:
            return self.client.lookup_bucket(path.bucket_name)
        except gcs_errors.ClientError:
            return None

    def get_bucket(self, path: PureGCSPath):
        try:
            return self.client.get_bucket(path.bucket_name)
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
    ) -> Generator[BucketEntry, None, None]:
        continuation_token = None
        if path is None or not path.bucket_name:
            for bucket in self.client.list_buckets():
                yield BucketEntry(bucket.name, is_dir=True)
            return
        sep = path._flavour.sep
        bucket = self.lookup_bucket(path)
        if bucket is None:
            return
        while True:
            if continuation_token:
                response = self.client.list_blobs(
                    bucket, prefix=prefix, delimiter=sep, page_token=continuation_token,
                )
            else:
                response = self.client.list_blobs(bucket, prefix=prefix, delimiter=sep)
            for page in response.pages:
                for folder in list(page.prefixes):
                    full_name = folder[:-1] if folder.endswith(sep) else folder
                    name = full_name.split(sep)[-1]
                    yield BucketEntry(name, is_dir=True)
                for item in page:
                    yield BucketEntry(
                        name=item.name.split(sep)[-1],
                        is_dir=False,
                        size=item.size,
                        last_modified=item.updated,
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
    ) -> Generator[ClientBlob, None, None]:
        continuation_token = None
        bucket = self.lookup_bucket(path)
        if bucket is None:
            return
        while True:
            if continuation_token:
                response = self.client.list_blobs(
                    path.bucket_name,
                    prefix=prefix,
                    delimiter=delimiter,
                    page_token=continuation_token,
                )
            else:
                response = self.client.list_blobs(
                    path.bucket_name, prefix=prefix, delimiter=delimiter
                )
            for page in response.pages:
                for item in page:
                    yield item
            if response.next_page_token is None:
                break
            continuation_token = response.next_page_token

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        return self.client.create_bucket(path.bucket_name)
