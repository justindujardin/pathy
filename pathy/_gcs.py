from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional

from google.api_core import exceptions as gcs_errors  # type:ignore
from google.cloud.storage import Blob as GCSNativeBlob  # type:ignore
from google.cloud.storage import Bucket as GCSNativeBucket  # type:ignore
from google.cloud.storage import Client as GCSNativeClient  # type:ignore

from . import (
    Blob,
    Bucket,
    BucketClient,
    BucketEntry,
    ClientError,
    PathyScanDir,
    PurePathy,
    register_client,
)


class BucketEntryGCS(BucketEntry):
    bucket: "BucketGCS"
    raw: GCSNativeBlob  # type:ignore[override]


@dataclass
class BlobGCS(Blob):
    def delete(self) -> None:
        self.raw.delete()  # type:ignore

    def exists(self) -> bool:
        return self.raw.exists()  # type:ignore


@dataclass
class BucketGCS(Bucket):
    name: str
    bucket: GCSNativeBucket

    def get_blob(self, blob_name: str) -> Optional[BlobGCS]:
        assert isinstance(
            blob_name, str
        ), f"expected str blob name, but found: {type(blob_name)}"
        native_blob: Optional[Any] = None
        try:
            native_blob = self.bucket.get_blob(blob_name)  # type:ignore
        except gcs_errors.ClientError:
            pass
        if native_blob is None:
            return None
        return BlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,  # type:ignore
            name=native_blob.name,  # type:ignore
            raw=native_blob,
            size=native_blob.size,
            updated=int(native_blob.updated.timestamp()),  # type:ignore
        )

    def copy_blob(  # type:ignore[override]
        self, blob: BlobGCS, target: "BucketGCS", name: str
    ) -> Optional[BlobGCS]:
        assert blob.raw is not None, "raw storage.Blob instance required"
        native_blob: GCSNativeBlob = self.bucket.copy_blob(  # type: ignore
            blob.raw, target.bucket, name
        )
        if native_blob is None:
            return None
        return BlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,  # type:ignore
            name=native_blob.name,  # type:ignore
            raw=native_blob,
            size=native_blob.size,
            updated=int(native_blob.updated.timestamp()),  # type:ignore
        )

    def delete_blob(self, blob: BlobGCS) -> None:  # type:ignore[override]
        return self.bucket.delete_blob(blob.name)  # type:ignore

    def delete_blobs(self, blobs: List[BlobGCS]) -> None:  # type:ignore[override]
        return self.bucket.delete_blobs(blobs)  # type:ignore

    def exists(self) -> bool:
        try:
            return self.bucket.exists()  # type:ignore
        except gcs_errors.ClientError:
            return False


class BucketClientGCS(BucketClient):
    client: GCSNativeClient

    @property
    def client_params(self) -> Any:
        return dict(client=self.client)

    def __init__(self, **kwargs: Any) -> None:
        self.recreate(**kwargs)

    def recreate(self, **kwargs: Any) -> None:
        creds = kwargs["credentials"] if "credentials" in kwargs else None
        if creds is not None:
            kwargs["project"] = creds.project_id
        self.client = GCSNativeClient(**kwargs)

    def make_uri(self, path: PurePathy) -> str:
        return str(path)

    def create_bucket(  # type:ignore[override]
        self, path: PurePathy
    ) -> GCSNativeBucket:
        return self.client.create_bucket(path.root)  # type:ignore

    def delete_bucket(self, path: PurePathy) -> None:
        bucket = self.client.get_bucket(path.root)  # type:ignore
        bucket.delete()  # type:ignore

    def exists(self, path: PurePathy) -> bool:
        # Because we want all the parents of a valid blob (e.g. "directory" in
        # "directory/foo.file") to return True, we enumerate the blobs with a prefix
        # and compare the object names to see if they match a substring of the path
        key_name = str(path.key)
        try:
            for obj in self.list_blobs(path):
                if obj.name == key_name:
                    return True
                if obj.name.startswith(key_name + path._flavour.sep):  # type:ignore
                    return True
        except gcs_errors.ClientError:
            return False
        return False

    def lookup_bucket(self, path: PurePathy) -> Optional[BucketGCS]:
        try:
            native_bucket = self.client.bucket(path.root)  # type:ignore
            if native_bucket is not None:
                return BucketGCS(str(path.root), bucket=native_bucket)
        except gcs_errors.ClientError as err:
            print(err)

        return None

    def get_bucket(self, path: PurePathy) -> BucketGCS:
        try:
            native_bucket = self.client.bucket(path.root)  # type:ignore
            if native_bucket is not None:
                return BucketGCS(str(path.root), bucket=native_bucket)
            raise FileNotFoundError(f"Bucket {path.root} does not exist!")
        except gcs_errors.ClientError as e:
            raise ClientError(message=e.message, code=e.code)  # type:ignore

    def list_buckets(  # type:ignore[override]
        self, **kwargs: Dict[str, Any]
    ) -> Generator[GCSNativeBucket, None, None]:
        return self.client.list_buckets(**kwargs)  # type:ignore

    def scandir(  # type:ignore[override]
        self,
        path: Optional[PurePathy] = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> PathyScanDir:
        return _GCSScanDir(client=self, path=path, prefix=prefix, delimiter=delimiter)

    def list_blobs(
        self,
        path: PurePathy,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[BlobGCS, None, None]:
        continuation_token: Any = None
        bucket = self.lookup_bucket(path)
        if bucket is None:
            return
        while True:
            response: Any
            if continuation_token:
                response = self.client.list_blobs(  # type:ignore
                    path.root,
                    prefix=prefix,
                    delimiter=delimiter,
                    page_token=continuation_token,
                )
            else:
                response = self.client.list_blobs(  # type:ignore
                    path.root, prefix=prefix, delimiter=delimiter
                )

            page: Any
            item: Any
            for page in response.pages:  # type:ignore
                for item in page:
                    yield BlobGCS(
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


class _GCSScanDir(PathyScanDir):
    _client: BucketClientGCS

    def scandir(self) -> Generator[BucketEntryGCS, None, None]:
        continuation_token = None
        if self._path is None or not self._path.root:
            gcs_bucket: GCSNativeBucket
            for gcs_bucket in self._client.client.list_buckets():
                yield BucketEntryGCS(gcs_bucket.name, is_dir=True, raw=None)
            return
        sep = self._path._flavour.sep
        bucket = self._client.lookup_bucket(self._path)
        if bucket is None:
            return
        while True:
            if continuation_token:
                response = self._client.client.list_blobs(
                    bucket.name,
                    prefix=self._prefix,
                    delimiter=sep,
                    page_token=continuation_token,
                )
            else:
                response = self._client.client.list_blobs(
                    bucket.name, prefix=self._prefix, delimiter=sep
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


register_client("gs", BucketClientGCS)