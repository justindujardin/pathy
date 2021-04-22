has_gcs: bool
try:
    from ..gcs import BucketClientGCS

    has_gcs = bool(BucketClientGCS)
except ImportError:
    has_gcs = False
