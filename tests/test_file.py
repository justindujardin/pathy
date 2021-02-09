import pathlib
from typing import Optional

import mock
import pytest

from pathy import Pathy, get_client
from pathy.file import BlobFS, BucketClientFS, BucketFS


def raise_owner(self):
    raise KeyError("duh")


@pytest.mark.parametrize("adapter", ["fs"])
@mock.patch.object(pathlib.Path, "owner", raise_owner)
def test_file_get_blob_owner_key_error_protection(with_adapter):
    gs_bucket = Pathy("gs://my_bucket")
    gs_bucket.mkdir()
    path = gs_bucket / "blob.txt"
    path.write_text("hello world!")
    gcs_client: BucketClientFS = get_client("gs")
    bucket: BucketFS = gcs_client.get_bucket(gs_bucket)
    blob: Optional[BlobFS] = bucket.get_blob("blob.txt")
    assert blob.owner is None
