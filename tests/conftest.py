import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from pathy import Pathy, use_fs, use_fs_cache
from pathy.clients import set_client_params
from pathy.gcs import has_gcs

has_credentials = "GCS_CREDENTIALS" in os.environ

# Which adapters to use
TEST_ADAPTERS = ["gcs", "fs"] if has_credentials and has_gcs else ["fs"]


@pytest.fixture()
def bucket() -> str:
    return "pathy-tests-bucket"


@pytest.fixture()
def other_bucket() -> str:
    return "pathy-tests-bucket-other"


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


def credentials_from_env():
    """Extract a credentials instance from the GCS_CREDENTIALS env variable.

    You can specify the contents of a credentials JSON file or a file path
    that points to a JSON file.

    Raises AssertionError if the value is present but does not point to a file
    or valid JSON content."""
    if not has_gcs:
        return None

    creds = os.environ.get("GCS_CREDENTIALS", None)
    if creds is None:
        return None
    from google.oauth2 import service_account

    json_creds = None
    try:
        json_creds = json.loads(creds)
    except json.decoder.JSONDecodeError:
        pass

    # If not a file path, assume it's JSON content
    if json_creds is None:
        credentials = service_account.Credentials.from_service_account_file(creds)
    else:
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write(json.dumps(json_creds))
            credentials = service_account.Credentials.from_service_account_file(path)
        finally:
            os.remove(path)
    return credentials


@pytest.fixture()
def with_adapter(adapter: str, bucket: str, other_bucket: str):
    tmp_dir = None
    scheme = "gs"
    if adapter == "gcs":
        # Use GCS
        use_fs(False)
        credentials = credentials_from_env()
        if credentials is not None:
            set_client_params("gs", credentials=credentials)
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
    yield scheme

    if adapter == "fs" and tmp_dir is not None:
        # Cleanup fs temp folder
        shutil.rmtree(tmp_dir)
    use_fs(False)
    use_fs_cache(False)
