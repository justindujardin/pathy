from typing import Optional, List
from .client import BucketClient, ClientBucket, ClientBlob

try:
    from google.cloud import storage
    from google.api_core import exceptions as gcs_errors

    has_gcs = True
except ImportError:
    storage = None
    has_gcs = False


class BucketClientGCS(BucketClient):
    client: storage.Client

    def __init__(self, client: storage.Client = None):
        if client is None:
            client = storage.Client()
        self.client = client

    def lookup_bucket(self, bucket_name: Optional[str]) -> Optional[ClientBucket]:
        return self.client.lookup_bucket(bucket_name)

    def get_bucket(self, bucket_name: Optional[str]):
        return self.client.get_bucket(bucket_name)

    def list_buckets(self, **kwargs) -> List[ClientBucket]:
        return self.client.list_buckets(**kwargs)

    def list_blobs(
        self,
        bucket_name: Optional[str],
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> List[ClientBlob]:
        return self.client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)

    def create_bucket(self, bucket_name: Optional[str]) -> ClientBucket:
        return self.client.create_bucket(bucket_name)
