from dataclasses import dataclass, field
from typing import Optional, List, Generator, cast
from .client import BucketClient, ClientBucket, ClientBlob, ClientError, BucketEntry
from .base import PureGCSPath
import pathlib
import shutil
import os


class BucketEntryFS(BucketEntry["ClientBucketFS", pathlib.Path]):
    ...


@dataclass
class ClientBlobFS(ClientBlob["ClientBucketFS", pathlib.Path]):
    raw: pathlib.Path
    bucket: "ClientBucketFS"

    def delete(self) -> None:
        """Delete a file-based blob."""
        file_folder: str = os.path.dirname(self.raw)
        self.raw.unlink()
        # NOTE: in buckets folders only exist if a file is contained in them. Mimic
        # that behavior here by removing empty folders when the last file is removed.
        if len(os.listdir(file_folder)) == 0:
            shutil.rmtree(file_folder)

    def exists(self) -> bool:
        return self.raw.exists()


@dataclass
class ClientBucketFS(ClientBucket):
    name: str
    bucket: pathlib.Path

    def get_blob(self, blob_name: str) -> Optional[ClientBlobFS]:
        native_blob = self.bucket / blob_name
        if not native_blob.exists() or native_blob.is_dir():
            return None
        stat = native_blob.stat()
        return ClientBlobFS(
            bucket=self,
            owner=native_blob.owner(),
            name=blob_name,
            raw=native_blob,
            size=stat.st_size,
            updated=int(round(stat.st_mtime_ns * 1000)),
        )

    def copy_blob(
        self, blob: ClientBlobFS, target: "ClientBucketFS", name: str
    ) -> Optional[ClientBlobFS]:
        in_file = str(blob.bucket.bucket / blob.name)
        out_file = str(target.bucket / name)
        out_path = pathlib.Path(os.path.dirname(out_file))
        if not out_path.exists():
            out_path.mkdir(parents=True)
        shutil.copy(in_file, out_file)
        return None

    def delete_blob(self, blob: ClientBlobFS) -> None:
        blob.delete()

    def delete_blobs(self, blobs: List[ClientBlobFS]) -> None:
        for blob in blobs:
            blob.delete()


@dataclass
class BucketClientFS(BucketClient):
    # Root to store file-system buckets as children of
    root: pathlib.Path

    def full_path(self, path: PureGCSPath) -> pathlib.Path:
        if path.bucket_name is None:
            raise ValueError(f"Invalid bucket name for path: {path}")
        full_path = self.root.absolute() / path.bucket_name
        if path.key is not None:
            full_path = full_path / path.key
        return full_path

    def exists(self, path: PureGCSPath) -> bool:
        """Return True if the path exists as a file or folder on disk"""
        return self.full_path(path).exists()

    def is_dir(self, path: PureGCSPath) -> bool:
        return self.full_path(path).is_dir()

    def rmdir(self, path: PureGCSPath) -> None:
        full_path = self.full_path(path)
        return shutil.rmtree(str(full_path))

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
        if self.lookup_bucket(path) is None:
            raise ClientError(
                message=f'bucket "{path.bucket_name}" does not exist', code=404
            )

        full_path = self.full_path(path)
        if not full_path.exists():
            if full_path.name != "":
                full_path = full_path.parent
            full_path.mkdir(parents=True, exist_ok=True)
        return super().open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def make_uri(self, path: PureGCSPath) -> str:
        if not path.bucket_name:
            raise ValueError(
                f"cannot make a URI to an invalid bucket: {path.bucket_name}"
            )
        result = f"file://{self.root.absolute() / path.bucket_name / path.key}"
        return result

    def create_bucket(self, path: PureGCSPath) -> ClientBucket:
        if not path.bucket_name:
            raise ValueError(f"Invalid bucket name: {path.bucket_name}")
        bucket_path: pathlib.Path = self.root / path.bucket_name
        if bucket_path.exists():
            raise FileExistsError(f"Bucket already exists at: {bucket_path}")
        bucket_path.mkdir(parents=True, exist_ok=True)
        return ClientBucketFS(str(path.bucket_name), bucket=bucket_path)

    def delete_bucket(self, path: PureGCSPath) -> None:
        bucket_path: pathlib.Path = self.root / str(path.bucket_name)
        if bucket_path.exists():
            shutil.rmtree(bucket_path)

    def lookup_bucket(self, path: PureGCSPath) -> Optional[ClientBucketFS]:
        if path.bucket_name:
            bucket_path: pathlib.Path = self.root / path.bucket_name
            if bucket_path.exists():
                return ClientBucketFS(str(path.bucket_name), bucket=bucket_path)
        return None

    def get_bucket(self, path: PureGCSPath) -> ClientBucketFS:
        if not path.bucket_name:
            raise ValueError(f"path has an invalid bucket_name: {path.bucket_name}")
        bucket_path: pathlib.Path = self.root / path.bucket_name
        if bucket_path.is_dir():
            return ClientBucketFS(str(path.bucket_name), bucket=bucket_path)
        raise FileNotFoundError(f"Bucket {path.bucket_name} does not exist!")

    def list_buckets(self, **kwargs) -> Generator[ClientBucketFS, None, None]:
        for f in self.root.glob("*"):
            if f.is_dir():
                yield ClientBucketFS(f.name, f)

    def scandir(
        self,
        path: Optional[PureGCSPath] = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> Generator[BucketEntryFS, None, None]:
        if path is None or not path.bucket_name:
            for bucket in self.list_buckets():
                yield BucketEntryFS(bucket.name, is_dir=True, raw=None)
            return
        assert path is not None
        assert path.bucket_name is not None
        scan_path = self.root / path.bucket_name
        if prefix is not None:
            scan_path = scan_path / prefix
        for dir_entry in scan_path.glob("*"):
            if dir_entry.is_dir():
                yield BucketEntryFS(dir_entry.name, is_dir=True, raw=None)
            else:
                file_path = pathlib.Path(dir_entry)
                stat = file_path.stat()
                file_size = stat.st_size
                updated = int(round(stat.st_mtime_ns * 1000))
                blob: ClientBlob = ClientBlobFS(
                    self.get_bucket(path),
                    name=dir_entry.name,
                    size=file_size,
                    updated=updated,
                    owner=None,
                    raw=file_path,
                )
                yield BucketEntryFS(
                    name=dir_entry.name,
                    is_dir=False,
                    size=file_size,
                    last_modified=updated,
                    raw=blob,
                )

    def list_blobs(
        self,
        path: PureGCSPath,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[ClientBlobFS, None, None]:
        assert path.bucket_name is not None
        bucket = self.get_bucket(path)
        scan_path = self.root / path.bucket_name
        if prefix is not None:
            scan_path = scan_path / prefix
        elif prefix is not None:
            scan_path = scan_path / path.key

        # Path to a file
        if scan_path.exists() and not scan_path.is_dir():
            stat = scan_path.stat()
            file_size = stat.st_size
            updated = int(round(stat.st_mtime_ns * 1000))
            yield ClientBlobFS(
                bucket,
                name=scan_path.name,
                size=file_size,
                updated=updated,
                owner=None,
                raw=scan_path,
            )

        # Yield blobs for each file
        for file_path in scan_path.rglob("*"):
            if file_path.is_dir():
                continue
            stat = file_path.stat()
            file_size = stat.st_size
            updated = int(round(stat.st_mtime_ns * 1000))
            yield ClientBlobFS(
                bucket,
                name=f"{prefix if prefix is not None else ''}{file_path.name}",
                size=file_size,
                updated=updated,
                owner=None,
                raw=file_path,
            )
