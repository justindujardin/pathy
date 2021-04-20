from . import BucketClient, register_client


class GCSMissingClient(BucketClient):
    def __init__(self) -> None:
        raise AssertionError(
            """You are using the GCS functionality of Pathy without
having the required dependencies installed.

Please try installing them:

    pip install pathy[gcs]

"""
        )


has_gcs: bool
try:
    from ._gcs import BucketClientGCS

    has_gcs = bool(BucketClientGCS)
except ImportError:
    register_client("gs", GCSMissingClient)
    has_gcs = False


__all__ = ("has_gcs",)
