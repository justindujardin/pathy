import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator, Optional, Tuple

import pytest

from pathy import Pathy, set_client_params, use_fs, use_fs_cache

from . import has_gcs

has_credentials = "GCS_CREDENTIALS" in os.environ

# Which adapters to use
TEST_ADAPTERS = ["gcs", "s3", "fs"] if has_credentials and has_gcs else ["fs"]
# A unique identifier used to allow each python version and OS to test
# with separate bucket paths. This makes it possible to parallelize the
# tests.
ENV_ID = f"{sys.platform}.{sys.version_info.major}.{sys.version_info.minor}"


@pytest.fixture()
def bucket() -> str:
    return os.environ.get("PATHY_TEST_BUCKET", "pathy-tests-bucket")


@pytest.fixture()
def other_bucket() -> str:
    return os.environ.get("PATHY_TEST_BUCKET_OTHER", "pathy-tests-bucket-other")


@pytest.fixture()
def temp_folder() -> Generator[Path, None, None]:
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir)


@pytest.fixture()
def with_fs(temp_folder: Path) -> Generator[Path, None, None]:
    yield temp_folder
    # Turn off FS adapter
    use_fs(False)


def gcs_credentials_from_env() -> Optional[Any]:
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

    if json_creds is not None:
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write(json.dumps(json_creds))
            credentials = service_account.Credentials.from_service_account_file(path)
        finally:
            os.remove(path)
    else:
        # If not a JSON string, assume it's a JSON file path
        credentials = service_account.Credentials.from_service_account_file(creds)
    return credentials


def s3_credentials_from_env() -> Optional[Tuple[str, str]]:
    """Extract an access key ID and Secret from the environment."""
    if not has_gcs:
        return None

    access_key_id: Optional[str] = os.environ.get("PATHY_S3_ACCESS_ID", None)
    access_secret: Optional[str] = os.environ.get("PATHY_S3_ACCESS_SECRET", None)
    if access_key_id is None or access_secret is None:
        return None
    return (access_key_id, access_secret)


@pytest.fixture()
def with_adapter(
    adapter: str, bucket: str, other_bucket: str
) -> Generator[str, None, None]:
    tmp_dir = None
    scheme = "gs"
    if adapter == "gcs":
        # Use GCS
        use_fs(False)
        credentials = gcs_credentials_from_env()
        if credentials is not None:
            set_client_params("gs", credentials=credentials)
    elif adapter == "s3":
        scheme = "s3"
        # Use boto3
        use_fs(False)
        credentials = s3_credentials_from_env()
        if credentials is not None:
            key_id, key_secret = credentials
            set_client_params("s3", key_id=key_id, key_secret=key_secret)
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
