import json
import os
import random
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

import pytest

from pathy import PathlibPathEx, Pathy, set_client_params, use_fs, use_fs_cache

from . import azure_installed, gcs_installed, s3_installed

# A unique identifier used to allow each python version and OS to test
# with separate bucket paths. This makes it possible to parallelize the
# tests.
ENV_ID = f"{sys.platform}.{sys.version_info.major}.{sys.version_info.minor}"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-gcs",
        action="store_true",
        default=False,
        help="Run GCS tests (requires GCS_CREDENTIALS env var)",
    )
    parser.addoption(
        "--run-s3",
        action="store_true",
        default=False,
        help="Run S3 tests (requires PATHY_S3_ACCESS_ID and PATHY_S3_ACCESS_SECRET env vars)",
    )
    parser.addoption(
        "--run-azure",
        action="store_true",
        default=False,
        help="Run Azure tests (requires PATHY_AZURE_CONNECTION_STRING env var)",
    )


_REQUIRED_ENV_VARS = {
    "gcs": ["GCS_CREDENTIALS"],
    "s3": ["PATHY_S3_ACCESS_ID", "PATHY_S3_ACCESS_SECRET"],
    "azure": ["PATHY_AZURE_CONNECTION_STRING"],
}

_INSTALLED_FLAGS = {
    "gcs": lambda: gcs_installed,
    "s3": lambda: s3_installed,
    "azure": lambda: azure_installed,
}

_INSTALL_EXTRAS = {
    "gcs": "pathy[gcs]",
    "s3": "pathy[s3]",
    "azure": "pathy[azure]",
}


def get_test_adapters(config: pytest.Config) -> List[str]:
    adapters = ["fs"]
    for provider, flag in [
        ("gcs", "--run-gcs"),
        ("s3", "--run-s3"),
        ("azure", "--run-azure"),
    ]:
        if not config.getoption(flag):
            continue
        if not _INSTALLED_FLAGS[provider]():
            raise pytest.UsageError(
                f"{flag} was specified but {provider} dependencies are not installed. "
                f"Install with: uv sync --extra {provider}  (or: pip install {_INSTALL_EXTRAS[provider]})"
            )
        missing = [v for v in _REQUIRED_ENV_VARS[provider] if v not in os.environ]
        if missing:
            raise pytest.UsageError(
                f"{flag} was specified but required env var(s) not set: {', '.join(missing)}"
            )
        adapters.append(provider)
    return adapters


# Default for module-level imports (will be overridden by pytest session)
TEST_ADAPTERS: List[str] = ["fs"]


def pytest_configure(config: pytest.Config) -> None:
    global TEST_ADAPTERS
    TEST_ADAPTERS = get_test_adapters(config)


_CLOUD_ADAPTERS = {"gcs", "s3", "azure"}


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:  # type: ignore
    """Skip tests parametrized with cloud adapters that weren't requested."""
    active = set(TEST_ADAPTERS)
    skip_reasons = {
        "gcs": pytest.mark.skip(reason="GCS tests not requested (use --run-gcs)"),
        "s3": pytest.mark.skip(reason="S3 tests not requested (use --run-s3)"),
        "azure": pytest.mark.skip(reason="Azure tests not requested (use --run-azure)"),
    }
    for item in items:
        # Check if this test is parametrized with an adapter value
        if hasattr(item, "callspec") and "adapter" in item.callspec.params:
            adapter = item.callspec.params["adapter"]
            if adapter in _CLOUD_ADAPTERS and adapter not in active:
                item.add_marker(skip_reasons[adapter])


@pytest.fixture()
def bucket() -> str:
    return os.environ.get("PATHY_TEST_BUCKET", "pathy-tests-bucket")


@pytest.fixture()
def other_bucket() -> str:
    return os.environ.get("PATHY_TEST_BUCKET_OTHER", "pathy-tests-bucket-other")


@pytest.fixture()
def temp_folder() -> Generator[Path, None, None]:
    tmp_dir = tempfile.mkdtemp()
    yield PathlibPathEx(tmp_dir)
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
    creds = os.environ.get("GCS_CREDENTIALS", None)
    if creds is None:
        return None
    from google.oauth2.service_account import Credentials

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
            credentials = Credentials.from_service_account_file(path)  # type: ignore
        finally:
            os.remove(path)
    else:
        # If not a JSON string, assume it's a JSON file path
        credentials = Credentials.from_service_account_file(creds)  # type: ignore
    return credentials


def s3_credentials_from_env() -> Optional[Tuple[str, str]]:
    """Extract an access key ID and Secret from the environment."""
    access_key_id: Optional[str] = os.environ.get("PATHY_S3_ACCESS_ID", None)
    access_secret: Optional[str] = os.environ.get("PATHY_S3_ACCESS_SECRET", None)
    if access_key_id is None or access_secret is None:
        return None
    return (access_key_id, access_secret)


def azure_credentials_from_env() -> Optional[str]:
    """Extract a connection string from the environment."""
    connection_string: Optional[str] = os.environ.get(
        "PATHY_AZURE_CONNECTION_STRING", None
    )
    return connection_string


@pytest.fixture()
def with_adapter(
    adapter: str, bucket: str, other_bucket: str
) -> Generator[str, None, None]:
    tmp_dir = None
    scheme = "gs"
    if adapter == "gcs":
        # Use google-cloud-storage
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
    elif adapter == "azure":
        scheme = "azure"
        # Use azure-storage-blob
        use_fs(False)
        connection_string = azure_credentials_from_env()
        assert connection_string is not None, "expected valid connection_string in env"
        # Sometimes pass BlobServiceClient, and sometimes a connection string
        if bool(random.getrandbits(1)):
            from azure.storage.blob import BlobServiceClient

            service: BlobServiceClient = BlobServiceClient.from_connection_string(
                connection_string
            )
            set_client_params("azure", service=service)
        else:
            set_client_params("azure", connection_string=connection_string)

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
