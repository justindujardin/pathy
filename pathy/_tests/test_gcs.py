from unittest.mock import patch

import pytest

from pathy import Pathy, set_client_params

from . import has_gcs


def raise_default_creds_error() -> None:
    from google.auth.exceptions import DefaultCredentialsError

    raise DefaultCredentialsError()


@pytest.mark.parametrize("adapter", ["gcs"])
@patch("google.auth.default", raise_default_creds_error)
@pytest.mark.skipif(not has_gcs, reason="requires gcs")
def test_gcs_default_credentials_error_is_preserved(
    with_adapter: str, bucket: str
) -> None:
    from google.auth.exceptions import DefaultCredentialsError

    # Remove the default credentials (this will recreate the client and error)
    with pytest.raises(DefaultCredentialsError):
        set_client_params("gs")


@pytest.mark.parametrize("adapter", ["gcs"])
@pytest.mark.skipif(not has_gcs, reason="requires gcs")
def test_gcs_as_uri(with_adapter: str, bucket: str) -> None:
    assert Pathy("gs://etc/passwd").as_uri() == "gs://etc/passwd"
    assert Pathy("gs://etc/init.d/apache2").as_uri() == "gs://etc/init.d/apache2"
    assert Pathy("gs://bucket/key").as_uri() == "gs://bucket/key"
