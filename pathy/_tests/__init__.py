gcs_installed: bool
try:
    from ..gcs import BucketClientGCS

    gcs_installed = bool(BucketClientGCS)
except ImportError as e:
    print(f"GCS dependencies: {e}.")
    gcs_installed = False

s3_installed: bool
try:
    from ..s3 import BucketClientS3

    s3_installed = bool(BucketClientS3)
except ImportError as e:
    print(f"S3 dependencies: {e}.")
    s3_installed = False

azure_installed: bool
try:
    from ..azure import BucketClientAzure

    azure_installed = bool(BucketClientAzure)
except ImportError as e:
    print(f"Azure dependencies: {e}.")
    azure_installed = False
