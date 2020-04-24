from pathlib import Path


from pathy import PureGCSPath
from pathy.file import BucketClientFS


def test_client_create_bucket(temp_folder: Path):
    bucket_target = temp_folder / "foo"
    assert bucket_target.exists() is False
    cl = BucketClientFS(temp_folder)
    cl.create_bucket(PureGCSPath("gs://foo/"))
    assert bucket_target.exists() is True
