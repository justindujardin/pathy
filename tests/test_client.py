from pathlib import Path

import pytest

from pathy import Blob, Bucket, BucketClient, BucketClientFS, Pathy, PurePathy


def test_client_create_bucket(temp_folder: Path):
    bucket_target = temp_folder / "foo"
    assert bucket_target.exists() is False
    cl = BucketClientFS(temp_folder)
    cl.create_bucket(PurePathy("gs://foo/"))
    assert bucket_target.exists() is True


def test_client_base_bucket_raises_not_implemented():
    bucket = Bucket()
    blob = Blob(bucket, "foo", -1, -1, None, None)
    with pytest.raises(NotImplementedError):
        bucket.copy_blob(blob, bucket, "baz")
    with pytest.raises(NotImplementedError):
        bucket.get_blob("baz")
    with pytest.raises(NotImplementedError):
        bucket.delete_blobs([blob])
    with pytest.raises(NotImplementedError):
        bucket.delete_blob(blob)
    with pytest.raises(NotImplementedError):
        bucket.exists()


def test_client_base_blob_raises_not_implemented():
    blob = Blob(Bucket(), "foo", -1, -1, None, None)
    with pytest.raises(NotImplementedError):
        blob.delete()
    with pytest.raises(NotImplementedError):
        blob.exists()


def test_client_base_bucket_client_raises_not_implemented():
    client = BucketClient()
    with pytest.raises(NotImplementedError):
        client.lookup_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.get_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.list_buckets()
    with pytest.raises(NotImplementedError):
        client.list_blobs(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.scandir(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.create_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.delete_bucket(Pathy("gs://foo"))
