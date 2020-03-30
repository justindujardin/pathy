from pathlib import Path

import mock
import pytest
from google.auth.exceptions import DefaultCredentialsError

from gcspath import BucketClientFS, BucketsAccessor, get_fs_client, use_fs


def test_use_fs(with_fs: Path):
    assert get_fs_client() is None
    # Use the default path
    use_fs()
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root.exists()

    # Use with False disables the client
    use_fs(False)
    client = get_fs_client()
    assert client is None

    # Can use a given path
    use_fs(str(with_fs))
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root == with_fs

    use_fs(False)


@mock.patch("gcspath.gcs.BucketClientGCS", side_effect=DefaultCredentialsError())
def test_bucket_accessor_without_gcs(bucket_client_gcs_mock, temp_folder):
    accessor = BucketsAccessor()
    # Accessing the client lazily throws with no GCS or FS adapters configured
    with pytest.raises(AssertionError):
        accessor.client

    # Setting a fallback FS adapter fixes the problem
    use_fs(str(temp_folder))
    assert isinstance(accessor.client, BucketClientFS)
