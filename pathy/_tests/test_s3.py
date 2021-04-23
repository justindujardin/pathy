import pytest

from pathy import get_client


from . import has_s3

S3_ADAPTER = ["s3"]


@pytest.mark.skipif(has_s3, reason="requires s3 deps to NOT be installed")
def test_s3_import_error_missing_deps() -> None:
    with pytest.raises(ImportError):
        get_client("s3")
