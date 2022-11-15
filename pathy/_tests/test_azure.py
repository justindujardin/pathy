import pytest

from . import azure_testable

AZURE_ADAPTER = ["azure"]


@pytest.mark.parametrize("adapter", AZURE_ADAPTER)
@pytest.mark.skipif(not azure_testable, reason="requires s3")
def test_azure_recreate_expected_args(with_adapter: str) -> None:
    from pathy.azure import BucketClientAzure

    # Must specify either service, or connection_string
    with pytest.raises(ValueError):
        BucketClientAzure()
