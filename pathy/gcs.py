from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional

from .base import (
    Blob,
    Bucket,
    BucketClient,
    BucketEntry,
    ClientError,
    PathyScanDir,
    PurePathy,
)

try:
    from google.api_core import exceptions as gcs_errors  # type:ignore
    from google.auth.exceptions import DefaultCredentialsError  # type:ignore
    from google.cloud.storage import Blob as GCSNativeBlob  # type:ignore
    from google.cloud.storage import Bucket as GCSNativeBucket  # type:ignore
    from google.cloud.storage import Client as GCSNativeClient  # type:ignore

    has_gcs = True
except ImportError:
    GCSNativeBlob = Any
    DefaultCredentialsError = BaseException
    gcs_errors = Any
    GCSNativeBucket = Any
    GCSNativeClient = Any
    has_gcs = False

_MISSING_DEPS = """You are using the GCS functionality of Pathy without
having the required dependencies installed.

Please try installing them:

    pip install pathy[gcs]

"""


class BucketEntryGCS(BucketEntry["BucketGCS", GCSNativeBlob]):
    ...


@dataclass
class BlobGCS(Blob[GCSNativeBucket, GCSNativeBlob]):
    def delete(self) -> None:
        self.raw.delete()

    def exists(self) -> bool:
        return self.raw.exists()


@dataclass
class BucketGCS(Bucket):
    name: str
    bucket: GCSNativeBucket

    def get_blob(self, blob_name: str) -> Optional[BlobGCS]:
        assert isinstance(
            blob_name, str
        ), f"expected str blob name, but found: {type(blob_name)}"
        native_blob = None
        try:
            native_blob = self.bucket.get_blob(blob_name)
        except gcs_errors.ClientError:
            pass
        if native_blob is None:
            return None
        return BlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,
            name=native_blob.name,
            raw=native_blob,
            size=native_blob.size,
            updated=int(native_blob.updated.timestamp()),
        )

    def copy_blob(  # type:ignore[override]
        self, blob: BlobGCS, target: "BucketGCS", name: str
    ) -> Optional[BlobGCS]:
        assert blob.raw is not None, "raw storage.Blob instance required"
        native_blob = self.bucket.copy_blob(blob.raw, target.bucket, name)
        if native_blob is None:
            return None
        return BlobGCS(
            bucket=self.bucket,
            owner=native_blob.owner,
            name=native_blob.name,
            raw=native_blob,
            size=native_blob.size,
            updated=int(native_blob.updated.timestamp()),
        )

    def delete_blob(self, blob: BlobGCS) -> None:  # type:ignore[override]
        return self.bucket.delete_blob(blob.name)

    def delete_blobs(self, blobs: List[BlobGCS]) -> None:  # type:ignore[override]
        return self.bucket.delete_blobs(blobs)

    def exists(self) -> bool:
        try:
            return self.bucket.exists()
        except gcs_errors.ClientError:
            return False


class BucketClientGCS(BucketClient):
    client: Optional[GCSNativeClient]

    @property
    def client_params(self) -> Any:
        return dict(client=self.client)

    def __init__(self, **kwargs: Any) -> None:
        self.recreate(**kwargs)

    def recreate(self, **kwargs: Any) -> None:
        creds = kwargs["credentials"] if "credentials" in kwargs else None
        if creds is not None:
            kwargs["project"] = creds.project_id
        try:
            self.client = GCSNativeClient(**kwargs)
        except TypeError:
            # TypeError is raised if the imports for GCSNativeClient fail and are
            #  assigned to Any, which is not callable.
            self.client = None

    def make_uri(self, path: PurePathy) -> str:
        return str(path)

    def create_bucket(self, path: PurePathy) -> Bucket:
        assert self.client is not None, _MISSING_DEPS
        return self.client.create_bucket(path.root)

    def delete_bucket(self, path: PurePathy) -> None:
        assert self.client is not None, _MISSING_DEPS
        bucket = self.client.get_bucket(path.root)
        bucket.delete()

    def exists(self, path: PurePathy) -> bool:
        # Because we want all the parents of a valid blob (e.g. "directory" in
        # "directory/foo.file") to return True, we enumerate the blobs with a prefix
        # and compare the object names to see if they match a substring of the path
        key_name = str(path.key)
        try:
            for obj in self.list_blobs(path):
                if obj.name == key_name:
                    return True
                if obj.name.startswith(key_name + path._flavour.sep):
                    return True
        except gcs_errors.ClientError:
            return False
        return False

    def lookup_bucket(self, path: PurePathy) -> Optional[BucketGCS]:
        assert self.client is not None, _MISSING_DEPS
        try:
            native_bucket = self.client.bucket(path.root)
            if native_bucket is not None:
                return BucketGCS(str(path.root), bucket=native_bucket)
        except gcs_errors.ClientError as err:
            print(err)

        return None

    def get_bucket(self, path: PurePathy) -> BucketGCS:
        assert self.client is not None, _MISSING_DEPS
        try:
            native_bucket = self.client.bucket(path.root)
            if native_bucket is not None:
                return BucketGCS(str(path.root), bucket=native_bucket)
            raise FileNotFoundError(f"Bucket {path.root} does not exist!")
        except gcs_errors.ClientError as e:
            raise ClientError(message=e.message, code=e.code)

    def list_buckets(
        self, **kwargs: Dict[str, Any]
    ) -> Generator[GCSNativeBucket, None, None]:
        assert self.client is not None, _MISSING_DEPS
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
        assert self.client is not None, _MISSING_DEPS
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
        assert self._client.client is not None, _MISSING_DEPS
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
