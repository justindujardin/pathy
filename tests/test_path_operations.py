import sys
from pathlib import Path

import mock
import pytest
from google.cloud import storage

from gcspath import GCSPath, PureGCSPath, StatResult, _gcs_accessor

# todo: test samefile/touch/write_text/write_bytes method
# todo: test security and boto config changes
# todo: test open method check R/W bytes/unicode


# todo(jd): replace global test-bucket with mock or generate buckets and call these e2e tests
bucket = "gcsbucket-test-dev"
other_bucket = "gcsbucket-test-dev-other"


@pytest.fixture()
def gcs_mock():
    client = mock.create_autospec(storage.Client)
    yield client


def test_path_support():
    assert PureGCSPath in GCSPath.mro()
    assert Path in GCSPath.mro()


def test_stat():
    path = GCSPath("fake-bucket-1234-0987/fake-key")
    with pytest.raises(ValueError):
        path.stat()
    test_file = "gs://gcsbucket-test-dev/foo.txt"
    client = storage.Client()
    blob = storage.Blob.from_string(test_file)
    blob.upload_from_string("a-a-a-a-a-a-a", client=client)
    path = GCSPath.from_uri(test_file)
    stat = path.stat()
    assert isinstance(stat, StatResult)
    assert stat == StatResult(size=blob.size, last_modified=blob.updated)
    assert GCSPath("/test-bucket").stat() is None


def test_exists():
    path = GCSPath("./fake-key")
    with pytest.raises(ValueError):
        path.exists()

    # GCS buckets are globally unique, "test-bucket" exists so this
    # raises an access error.
    assert GCSPath("/test-bucket/fake-key").exists() is False
    # invalid bucket name
    assert GCSPath("/unknown-bucket-name-123987519875419").exists() is False
    # valid bucket with invalid object
    assert GCSPath("/gcsbucket-test-dev/not_found_lol_nice.txt").exists() is False

    test_path = "/gcsbucket-test-dev/directory/foo.txt"
    test_gs_file = f"gs:/{test_path}"
    client = storage.Client()
    blob = storage.Blob.from_string(test_gs_file)
    blob.upload_from_string("---", client=client)
    path = GCSPath(test_path)
    assert path.exists()
    for parent in path.parents:
        assert parent.exists()


def test_glob():
    client = storage.Client()
    for i in range(3):
        blob = storage.Blob.from_string(f"gs://{bucket}/glob/{i}.file")
        blob.upload_from_string("---", client=client)
    for i in range(2):
        blob = storage.Blob.from_string(f"gs://{bucket}/glob/{i}/dir/file.txt")
        blob.upload_from_string("---", client=client)

    assert list(GCSPath(f"/{bucket}/glob/").glob("*.test")) == []
    assert list(GCSPath(f"/{bucket}/glob/").glob("*.file")) == [
        GCSPath("/gcsbucket-test-dev/glob/0.file"),
        GCSPath("/gcsbucket-test-dev/glob/1.file"),
        GCSPath("/gcsbucket-test-dev/glob/2.file"),
    ]
    assert list(GCSPath(f"/{bucket}/glob/0/").glob("*/*.txt")) == [
        GCSPath("/gcsbucket-test-dev/glob/0/dir/file.txt"),
    ]
    assert sorted(GCSPath.from_uri(f"gs://{bucket}").glob("*lob/")) == [
        GCSPath(f"/{bucket}/glob"),
    ]
    # Recursive matches
    assert list(GCSPath(f"/{bucket}/glob/").glob("**/*.txt")) == [
        GCSPath("/gcsbucket-test-dev/glob/0/dir/file.txt"),
        GCSPath("/gcsbucket-test-dev/glob/1/dir/file.txt"),
    ]
    # rglob adds the **/ for you
    assert list(GCSPath(f"/{bucket}/glob/").rglob("*.txt")) == [
        GCSPath("/gcsbucket-test-dev/glob/0/dir/file.txt"),
        GCSPath("/gcsbucket-test-dev/glob/1/dir/file.txt"),
    ]


def test_is_dir():
    client = storage.Client()
    target_file = f"/{bucket}/is_dir/subfolder/another/my.file"
    blob = storage.Blob.from_string(f"gs:/{target_file}")
    blob.upload_from_string("---", client=client)
    path = GCSPath(target_file)
    assert path.is_dir() is False
    for parent in path.parents:
        assert parent.is_dir() is True


def test_is_file():
    client = storage.Client()
    target_file = f"/{bucket}/is_file/subfolder/another/my.file"
    blob = storage.Blob.from_string(f"gs:/{target_file}")
    blob.upload_from_string("---", client=client)
    path = GCSPath(target_file)
    # The full file is a file
    assert path.is_file() is True
    # Each parent node in the path is only a directory
    for parent in path.parents:
        assert parent.is_file() is False


def test_iterdir():
    client = storage.Client()
    # (n) files in a folder
    for i in range(2):
        blob = storage.Blob.from_string(f"gs://{bucket}/iterdir/{i}.file")
        blob.upload_from_string("---", client=client)
    # 1 file in a subfolder
    blob = storage.Blob.from_string(f"gs://{bucket}/iterdir/sub/file.txt")
    blob.upload_from_string("---", client=client)

    path = GCSPath(f"/{bucket}/iterdir/")
    assert sorted(path.iterdir()) == [
        GCSPath(f"/{bucket}/iterdir/0.file"),
        GCSPath(f"/{bucket}/iterdir/1.file"),
        GCSPath(f"/{bucket}/iterdir/sub"),
    ]


def test_open_for_read():
    client = storage.Client()
    blob = storage.Blob.from_string(f"gs://{bucket}/read/file.txt")
    blob.upload_from_string("---", client=client)
    path = GCSPath(f"/{bucket}/read/file.txt")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


def test_open_for_write():
    path = GCSPath(f"/{bucket}/write/file.txt")
    with path.open(mode="w") as file_obj:
        file_obj.write("---")
        file_obj.writelines([b"---"])
    path = GCSPath(f"/{bucket}/write/file.txt")
    with path.open() as file_obj:
        assert file_obj.read() == "------"


def test_open_binary_read():
    path = GCSPath(f"/{bucket}/read_binary/file.txt")
    path.write_bytes(b"---")
    with path.open(mode="br") as file_obj:
        assert file_obj.readlines() == [b"---"]
    with path.open(mode="rb") as file_obj:
        assert file_obj.readline() == b"---"
        assert file_obj.readline() == b""


def test_readwrite_text():
    path = GCSPath(f"/{bucket}/write_text/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


def test_readwrite_bytes():
    path = GCSPath(f"/{bucket}/write_bytes/file.txt")
    path.write_bytes(b"---")
    assert path.read_bytes() == b"---"


def test_readwrite_lines():
    path = GCSPath(f"/{bucket}/write_text/file.txt")
    with path.open("w") as file_obj:
        file_obj.writelines([b"---"])
    with path.open("r") as file_obj:
        assert file_obj.readlines() == ["---"]
    with path.open("rt") as file_obj:
        assert file_obj.readline() == "---"


def test_owner():
    # Raises for invalid file
    with pytest.raises(FileNotFoundError):
        GCSPath(f"/{bucket}/write_text/not_a_valid_blob").owner()

    path = GCSPath(f"/{bucket}/write_text/file.txt")
    path.write_text("---")
    # TODO: How to set file owner to non-None in GCS? Then assert here.
    assert path.owner() is None


def test_rename_files_in_bucket():
    # Rename a single file
    GCSPath(f"/{bucket}/rename/file.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/file.txt").rename(f"/{bucket}/rename/other.txt")
    assert not GCSPath(f"/{bucket}/rename/file.txt").exists()
    assert GCSPath(f"/{bucket}/rename/other.txt").is_file()


def test_rename_files_across_buckets():
    # Rename a single file across buckets
    GCSPath(f"/{bucket}/rename/file.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/file.txt").rename(f"/{other_bucket}/rename/other.txt")
    assert not GCSPath(f"/{bucket}/rename/file.txt").exists()
    assert GCSPath(f"/{other_bucket}/rename/other.txt").is_file()


def test_rename_folders_in_bucket():
    # Rename a folder in the same bucket
    GCSPath(f"/{bucket}/rename/folder/one.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/folder/two.txt").write_text("---")
    path = GCSPath(f"/{bucket}/rename/folder/")
    new_path = GCSPath(f"/{bucket}/rename/other/")
    path.rename(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert GCSPath(f"/{bucket}/rename/other/one.txt").is_file()
    assert GCSPath(f"/{bucket}/rename/other/two.txt").is_file()


def test_rename_folders_across_buckets():
    # Rename a folder across buckets
    GCSPath(f"/{bucket}/rename/folder/one.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/folder/two.txt").write_text("---")
    path = GCSPath(f"/{bucket}/rename/folder/")
    new_path = GCSPath(f"/{other_bucket}/rename/other/")
    path.rename(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert GCSPath(f"/{other_bucket}/rename/other/one.txt").is_file()
    assert GCSPath(f"/{other_bucket}/rename/other/two.txt").is_file()


def test_replace_files_in_bucket():
    # replace a single file
    GCSPath(f"/{bucket}/replace/file.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/file.txt").replace(f"/{bucket}/replace/other.txt")
    assert not GCSPath(f"/{bucket}/replace/file.txt").exists()
    assert GCSPath(f"/{bucket}/replace/other.txt").is_file()


def test_replace_files_across_buckets():
    # Rename a single file across buckets
    GCSPath(f"/{bucket}/replace/file.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/file.txt").replace(f"/{other_bucket}/replace/other.txt")
    assert not GCSPath(f"/{bucket}/replace/file.txt").exists()
    assert GCSPath(f"/{other_bucket}/replace/other.txt").is_file()


def test_replace_folders_in_bucket():
    # Rename a folder in the same bucket
    GCSPath(f"/{bucket}/replace/folder/one.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/folder/two.txt").write_text("---")
    path = GCSPath(f"/{bucket}/replace/folder/")
    new_path = GCSPath(f"/{bucket}/replace/other/")
    path.replace(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert GCSPath(f"/{bucket}/replace/other/one.txt").is_file()
    assert GCSPath(f"/{bucket}/replace/other/two.txt").is_file()


def test_replace_folders_across_buckets():
    # Rename a folder across buckets
    GCSPath(f"/{bucket}/replace/folder/one.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/folder/two.txt").write_text("---")
    path = GCSPath(f"/{bucket}/replace/folder/")
    new_path = GCSPath(f"/{other_bucket}/replace/other/")
    path.replace(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert GCSPath(f"/{other_bucket}/replace/other/one.txt").is_file()
    assert GCSPath(f"/{other_bucket}/replace/other/two.txt").is_file()


# def test_rmdir(gcs_mock):
#     s3 = boto3.resource("s3")
#     s3.create_bucket(Bucket="test-bucket")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/conf.py")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/make.bat")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/index.rst")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/Makefile")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/_templates/11conf.py")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/_build/22conf.py")
#     object_summary.put(Body=b"test data")
#     object_summary = s3.ObjectSummary("test-bucket", "docs/_static/conf.py")
#     object_summary.put(Body=b"test data")

#     conf_path = GCSPath("/test-bucket/docs/_templates")
#     assert conf_path.is_dir()
#     conf_path.rmdir()
#     assert not conf_path.exists()

#     path = GCSPath("/test-bucket/docs/")
#     path.rmdir()
#     assert not path.exists()


# def test_mkdir(gcs_mock):
#     s3 = boto3.resource("s3")

#     GCSPath("/test-bucket/").mkdir()

#     assert s3.Bucket("test-bucket") in s3.buckets.all()

#     GCSPath("/test-bucket/").mkdir(exist_ok=True)

#     with pytest.raises(FileExistsError):
#         GCSPath("/test-bucket/").mkdir(exist_ok=False)

#     with pytest.raises(FileNotFoundError):
#         GCSPath("/test-second-bucket/test-directory/file.name").mkdir()

#     GCSPath("/test-second-bucket/test-directory/file.name").mkdir(parents=True)

#     assert s3.Bucket("test-second-bucket") in s3.buckets.all()
