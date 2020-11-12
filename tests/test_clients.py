import time
from pathlib import Path

import pytest

from pathy import Pathy, get_client
from pathy.clients import get_fs_client, use_fs, use_fs_cache
from pathy.file import BucketClientFS
from pathy.gcs import BucketClientGCS

from .conftest import TEST_ADAPTERS


def test_clients_get_client_works_with_builtin_schems():
    assert isinstance(get_client("gs"), BucketClientGCS)
    assert isinstance(get_client("file"), BucketClientFS)
    assert isinstance(get_client(""), BucketClientFS)


def test_clients_get_client_errors_with_unknown_scheme():
    with pytest.raises(ValueError):
        get_client("foo")


def test_clients_use_fs(with_fs: Path):
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

    # Can use a pathlib.Path
    use_fs(with_fs)
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root == with_fs

    use_fs(False)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_use_fs_cache(with_adapter, with_fs: str, bucket: str):
    path = Pathy(f"gs://{bucket}/directory/foo.txt")
    path.write_text("---")
    assert isinstance(path, Pathy)
    with pytest.raises(ValueError):
        Pathy.to_local(path)

    use_fs_cache(with_fs)
    source_file: Path = Pathy.to_local(path)
    foo_timestamp = Path(f"{source_file}.time")
    assert foo_timestamp.exists()
    orig_cache_time = foo_timestamp.read_text()

    # fetch from the local cache
    cached_file: Path = Pathy.to_local(path)
    assert cached_file == source_file
    cached_cache_time = foo_timestamp.read_text()
    assert orig_cache_time == cached_cache_time, "cached blob timestamps should match"

    # Update the blob
    time.sleep(0.1)
    path.write_text('{ "cool" : true }')

    # Fetch the updated blob
    Pathy.to_local(path)
    updated_cache_time = foo_timestamp.read_text()
    assert updated_cache_time != orig_cache_time, "cached timestamp did not change"
