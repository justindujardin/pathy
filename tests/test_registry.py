import pytest

from pathy import get_client
from pathy.file import BucketClientFS
from pathy.gcs import BucketClientGCS


def test_registry_get_client_works_with_builtin_schems():
    assert isinstance(get_client("gs"), BucketClientGCS)
    assert isinstance(get_client("file"), BucketClientFS)


def test_registry_get_client_errors_with_unknown_scheme():
    with pytest.raises(ValueError):
        get_client("foo")
