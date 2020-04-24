import os
import shutil
import tempfile
from pathlib import Path

import pytest
from pathy import Pathy, use_fs, use_fs_cache


# TODO: set this up with a service account for the CI
has_credentials = "CI" not in os.environ

# Which adapters to use
TEST_ADAPTERS = ["gcs", "fs"] if has_credentials else ["fs"]


@pytest.fixture()
def bucket() -> str:
    return "pathy-tests-1"


@pytest.fixture()
def other_bucket() -> str:
    return "pathy-tests-2"


@pytest.fixture()
def temp_folder():
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir)


@pytest.fixture()
def with_fs(temp_folder):
    yield temp_folder
    # Turn off FS adapter
    use_fs(False)


@pytest.fixture()
def with_adapter(adapter: str, bucket: str, other_bucket: str):
    tmp_dir = None
    if adapter == "gcs":
        # Use GCS (with system credentials)
        use_fs(False)
    elif adapter == "fs":
        # Use local file-system in a temp folder
        tmp_dir = tempfile.mkdtemp()
        use_fs(tmp_dir)
        bucket_one = Pathy.from_bucket(bucket)
        if not bucket_one.exists():
            bucket_one.mkdir()
        bucket_two = Pathy.from_bucket(other_bucket)
        if not bucket_two.exists():
            bucket_two.mkdir()
    else:
        raise ValueError("invalid adapter, nothing is configured")
    # execute the test
    yield

    if adapter == "fs" and tmp_dir is not None:
        # Cleanup fs temp folder
        shutil.rmtree(tmp_dir)
    use_fs(False)
    use_fs_cache(False)
