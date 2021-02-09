import os
import pathlib
import shutil
from dataclasses import dataclass, field
from io import DEFAULT_BUFFER_SIZE
from typing import Any, Dict, Generator, List, Optional

from .base import (
    Blob,
    Bucket,
    BucketClient,
    BucketEntry,
    ClientError,
    Pathy,
    PathyScanDir,
    PurePathy,
    StreamableType,
)


class BucketEntryFS(BucketEntry["BucketFS", pathlib.Path]):
    ...


@dataclass
class BlobFS(Blob["BucketFS", pathlib.Path]):
    raw: pathlib.Path
    bucket: "BucketFS"

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
class BucketFS(Bucket):
    name: str
    bucket: pathlib.Path

    def get_blob(self, blob_name: str) -> Optional[BlobFS]:  # type:ignore[override]
        native_blob = self.bucket / blob_name
        if not native_blob.exists() or native_blob.is_dir():
            return None
        stat = native_blob.stat()
        # path.owner() raises KeyError if the owner's UID isn't known
        #
        # https://docs.python.org/3/library/pathlib.html#pathlib.Path.owner
        owner: Optional[str]
        try:
            owner = native_blob.owner()
        except KeyError:
            owner = None
        return BlobFS(
            bucket=self,
            owner=owner,
            name=blob_name,
            raw=native_blob,
            size=stat.st_size,
            updated=int(round(stat.st_mtime)),
        )

    def copy_blob(  # type:ignore[override]
        self, blob: BlobFS, target: "BucketFS", name: str
    ) -> Optional[BlobFS]:
        in_file = str(blob.bucket.bucket / blob.name)
        out_file = str(target.bucket / name)
        out_path = pathlib.Path(os.path.dirname(out_file))
        if not out_path.exists():
            out_path.mkdir(parents=True)
        shutil.copy(in_file, out_file)
        return None

    def delete_blob(self, blob: BlobFS) -> None:  # type:ignore[override]
        blob.delete()

    def delete_blobs(self, blobs: List[BlobFS]) -> None:  # type:ignore[override]
        for blob in blobs:
            blob.delete()

    def exists(self) -> bool:
        return self.bucket.exists()


@dataclass
class BucketClientFS(BucketClient):
    # Root to store file-system buckets as children of
    root: pathlib.Path = field(default_factory=lambda: pathlib.Path("/tmp/"))

    def full_path(self, path: Pathy) -> pathlib.Path:
        if path.root is None:
            raise ValueError(f"Invalid bucket name for path: {path}")
        full_path = self.root.absolute() / path.root
        if path.key is not None:
            full_path = full_path / path.key
        return full_path

    def exists(self, path: Pathy) -> bool:
        """Return True if the path exists as a file or folder on disk"""
        return self.full_path(path).exists()

    def is_dir(self, path: Pathy) -> bool:
        return self.full_path(path).is_dir()

    def rmdir(self, path: Pathy) -> None:
        full_path = self.full_path(path)
        return shutil.rmtree(str(full_path))

    def open(
        self,
        path: Pathy,
        *,
        mode: str = "r",
        buffering: int = DEFAULT_BUFFER_SIZE,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ) -> StreamableType:
        if self.lookup_bucket(path) is None:
            raise ClientError(message=f'bucket "{path.root}" does not exist', code=404)

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

    def make_uri(self, path: PurePathy) -> str:
        if not path.root:
            raise ValueError(f"cannot make a URI to an invalid bucket: {path.root}")
        full_path = self.root.absolute() / path.root
        if path.key is not None:
            full_path /= path.key
        result = f"file://{full_path}"
        return result

    def create_bucket(self, path: PurePathy) -> Bucket:
        if not path.root:
            raise ValueError(f"Invalid bucket name: {path.root}")
        bucket_path: pathlib.Path = self.root / path.root
        if bucket_path.exists():
            raise FileExistsError(f"Bucket already exists at: {bucket_path}")
        bucket_path.mkdir(parents=True, exist_ok=True)
        return BucketFS(str(path.root), bucket=bucket_path)

    def delete_bucket(self, path: PurePathy) -> None:
        bucket_path: pathlib.Path = self.root / str(path.root)
        if bucket_path.exists():
            shutil.rmtree(bucket_path)

    def lookup_bucket(self, path: PurePathy) -> Optional[BucketFS]:
        if path.root:
            bucket_path: pathlib.Path = self.root / path.root
            if bucket_path.exists():
                return BucketFS(str(path.root), bucket=bucket_path)
        return None

    def get_bucket(self, path: PurePathy) -> BucketFS:
        if not path.root:
            raise ValueError(f"path has an invalid bucket_name: {path.root}")
        bucket_path: pathlib.Path = self.root / path.root
        if bucket_path.is_dir():
            return BucketFS(str(path.root), bucket=bucket_path)
        raise FileNotFoundError(f"Bucket {path.root} does not exist!")

    def list_buckets(self, **kwargs: Dict[str, Any]) -> Generator[BucketFS, None, None]:
        for f in self.root.glob("*"):
            if f.is_dir():
                yield BucketFS(f.name, f)

    def scandir(
        self,
        path: Pathy = None,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
    ) -> PathyScanDir:
        return _FSScanDir(client=self, path=path, prefix=prefix, delimiter=delimiter)

    def list_blobs(
        self,
        path: PurePathy,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        include_dirs: bool = False,
    ) -> Generator[BlobFS, None, None]:
        assert path.root is not None
        bucket = self.get_bucket(path)
        scan_path = self.root / path.root
        if prefix is not None:
            scan_path = scan_path / prefix
        elif prefix is not None and path.key is not None:
            scan_path = scan_path / path.key

        # Path to a file
        if scan_path.exists() and not scan_path.is_dir():
            stat = scan_path.stat()
            file_size = stat.st_size
            updated = int(round(stat.st_mtime_ns * 1000))
            yield BlobFS(
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
            yield BlobFS(
                bucket,
                name=f"{prefix if prefix is not None else ''}{file_path.name}",
                size=file_size,
                updated=updated,
                owner=None,
                raw=file_path,
            )


class _FSScanDir(PathyScanDir):
    _client: BucketClientFS

    def scandir(self) -> Generator[BucketEntry[BucketFS, pathlib.Path], None, None]:
        if self._path is None or not self._path.root:
            for bucket in self._client.list_buckets():
                yield BucketEntryFS(bucket.name, is_dir=True, raw=None)
            return
        assert self._path is not None
        assert self._path.root is not None
        scan_path = self._client.root / self._path.root
        if self._prefix is not None:
            scan_path = scan_path / self._prefix
        for dir_entry in scan_path.glob("*"):
            if dir_entry.is_dir():
                yield BucketEntryFS(dir_entry.name, is_dir=True, raw=None)
            else:
                file_path = pathlib.Path(dir_entry)
                stat = file_path.stat()
                file_size = stat.st_size
                updated = int(round(stat.st_mtime))
                blob: Blob = BlobFS(
                    self._client.get_bucket(self._path),
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
