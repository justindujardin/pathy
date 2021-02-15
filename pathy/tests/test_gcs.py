from unittest.mock import patch

import pytest

from pathy import has_gcs, set_client_params


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
