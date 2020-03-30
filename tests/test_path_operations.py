import sys
from pathlib import Path
from uuid import uuid4

import mock
import pytest
from google.cloud import storage

from gcspath import GCSPath, PureGCSPath, BucketStat
import pytest
from pathlib import Path
import tempfile
import shutil
from gcspath import use_fs
import os

# todo: test samefile/touch/write_text/write_bytes method
# todo: test security and boto config changes
# todo: test open method check R/W bytes/unicode


# todo(jd): replace global test-bucket with mock or generate buckets and call these e2e tests
bucket = "gcspath-tests-1"
other_bucket = "gcspath-tests-2"

# TODO: set this up with a service account for the CI
has_credentials = "CI" not in os.environ

# Which adapters to use
TEST_ADAPTERS = ["gcs", "fs"] if has_credentials else ["fs"]


@pytest.fixture()
def bucket_():
    bucket = f"gcspath-test-{uuid4().hex}"
    yield bucket
    client = storage.Client()
    bucket = client.lookup_bucket(bucket)
    bucket.delete()


def test_path_support():
    assert PureGCSPath in GCSPath.mro()
    assert Path in GCSPath.mro()


@pytest.fixture()
def with_adapter(adapter: str):
    if adapter == "gcs":
        # Use GCS (with system credentials)
        use_fs(False)
    elif adapter == "fs":
        # Use local file-system in a temp folder
        tmp_dir = tempfile.mkdtemp()
        use_fs(tmp_dir)
        bucket_one = GCSPath(f"/{bucket}/")
        if not bucket_one.exists():
            bucket_one.mkdir()
        bucket_two = GCSPath(f"/{other_bucket}/")
        if not bucket_two.exists():
            bucket_two.mkdir()
    # execute the test
    yield

    if adapter == "fs":
        # Cleanup fs temp folder
        shutil.rmtree(tmp_dir)
    use_fs(False)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_stat(with_adapter):
    path = GCSPath("fake-bucket-1234-0987/fake-key")
    with pytest.raises(ValueError):
        path.stat()
    path = GCSPath(f"/{bucket}/foo.txt")
    path.write_text("a-a-a-a-a-a-a")
    stat = path.stat()
    assert isinstance(stat, BucketStat)
    assert stat.size > 0
    assert stat.last_modified > 0
    assert GCSPath("/test-bucket").stat() is None


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_exists(with_adapter):
    path = GCSPath("./fake-key")
    with pytest.raises(ValueError):
        path.exists()

    # GCS buckets are globally unique, "test-bucket" exists so this
    # raises an access error.
    assert GCSPath("/test-bucket/fake-key").exists() is False
    # invalid bucket name
    assert GCSPath("/unknown-bucket-name-123987519875419").exists() is False
    # valid bucket with invalid object
    assert GCSPath(f"/{bucket}/not_found_lol_nice.txt").exists() is False

    path = GCSPath(f"/{bucket}/directory/foo.txt")
    path.write_text("---")
    assert path.exists()
    for parent in path.parents:
        assert parent.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_glob(with_adapter):
    for i in range(3):
        path = GCSPath(f"/{bucket}/glob/{i}.file")
        path.write_text("---")
    for i in range(2):
        path = GCSPath(f"/{bucket}/glob/{i}/dir/file.txt")
        path.write_text("---")

    assert list(GCSPath(f"/{bucket}/glob/").glob("*.test")) == []
    assert sorted(list(GCSPath(f"/{bucket}/glob/").glob("*.file"))) == [
        GCSPath(f"/{bucket}/glob/0.file"),
        GCSPath(f"/{bucket}/glob/1.file"),
        GCSPath(f"/{bucket}/glob/2.file"),
    ]
    assert list(GCSPath(f"/{bucket}/glob/0/").glob("*/*.txt")) == [
        GCSPath(f"/{bucket}/glob/0/dir/file.txt"),
    ]
    assert sorted(GCSPath.from_uri(f"gs://{bucket}").glob("*lob/")) == [
        GCSPath(f"/{bucket}/glob"),
    ]
    # Recursive matches
    assert sorted(list(GCSPath(f"/{bucket}/glob/").glob("**/*.txt"))) == [
        GCSPath(f"/{bucket}/glob/0/dir/file.txt"),
        GCSPath(f"/{bucket}/glob/1/dir/file.txt"),
    ]
    # rglob adds the **/ for you
    assert sorted(list(GCSPath(f"/{bucket}/glob/").rglob("*.txt"))) == [
        GCSPath(f"/{bucket}/glob/0/dir/file.txt"),
        GCSPath(f"/{bucket}/glob/1/dir/file.txt"),
    ]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_unlink_path(with_adapter):
    path = GCSPath(f"/{bucket}/unlink/404.txt")
    with pytest.raises(FileNotFoundError):
        path.unlink()
    path = GCSPath(f"/{bucket}/unlink/foo.txt")
    path.write_text("---")
    assert path.exists()
    path.unlink()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_is_dir(with_adapter):
    path = GCSPath(f"/{bucket}/is_dir/subfolder/another/my.file")
    path.write_text("---")
    assert path.is_dir() is False
    for parent in path.parents:
        assert parent.is_dir() is True


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_is_file(with_adapter):
    path = GCSPath(f"/{bucket}/is_file/subfolder/another/my.file")
    path.write_text("---")
    # The full file is a file
    assert path.is_file() is True
    # Each parent node in the path is only a directory
    for parent in path.parents:
        assert parent.is_file() is False


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_iterdir(with_adapter):
    # (n) files in a folder
    for i in range(2):
        path = GCSPath(f"/{bucket}/iterdir/{i}.file")
        path.write_text("---")

    # 1 file in a subfolder
    path = GCSPath(f"/{bucket}/iterdir/sub/file.txt")
    path.write_text("---")

    path = GCSPath(f"/{bucket}/iterdir/")
    assert sorted(path.iterdir()) == [
        GCSPath(f"/{bucket}/iterdir/0.file"),
        GCSPath(f"/{bucket}/iterdir/1.file"),
        GCSPath(f"/{bucket}/iterdir/sub"),
    ]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_open_for_read(with_adapter):
    path = GCSPath(f"/{bucket}/read/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_open_for_write(with_adapter):
    path = GCSPath(f"/{bucket}/write/file.txt")
    with path.open(mode="w") as file_obj:
        file_obj.write("---")
        file_obj.writelines(["---"])
    path = GCSPath(f"/{bucket}/write/file.txt")
    with path.open() as file_obj:
        assert file_obj.read() == "------"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_open_binary_read(with_adapter):
    path = GCSPath(f"/{bucket}/read_binary/file.txt")
    path.write_bytes(b"---")
    with path.open(mode="rb") as file_obj:
        assert file_obj.readlines() == [b"---"]
    with path.open(mode="rb") as file_obj:
        assert file_obj.readline() == b"---"
        assert file_obj.readline() == b""


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_readwrite_text(with_adapter):
    path = GCSPath(f"/{bucket}/write_text/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_readwrite_bytes(with_adapter):
    path = GCSPath(f"/{bucket}/write_bytes/file.txt")
    path.write_bytes(b"---")
    assert path.read_bytes() == b"---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_readwrite_lines(with_adapter):
    path = GCSPath(f"/{bucket}/write_text/file.txt")
    with path.open("w") as file_obj:
        file_obj.writelines(["---"])
    with path.open("r") as file_obj:
        assert file_obj.readlines() == ["---"]
    with path.open("rt") as file_obj:
        assert file_obj.readline() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_owner(with_adapter):
    # Raises for invalid file
    with pytest.raises(FileNotFoundError):
        GCSPath(f"/{bucket}/write_text/not_a_valid_blob").owner()

    path = GCSPath(f"/{bucket}/write_text/file.txt")
    path.write_text("---")
    # TODO: How to set file owner to non-None in GCS? Then assert here.
    #
    # NOTE: The owner is always set when using the filesystem adapter, so
    #       we can't assert the same behavior here until we fix the above
    #       todo comment.
    try:
        path.owner()
    except BaseException:
        pytest.fail("Should not raise")


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_rename_files_in_bucket(with_adapter):
    # Rename a single file
    GCSPath(f"/{bucket}/rename/file.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/file.txt").rename(f"/{bucket}/rename/other.txt")
    assert not GCSPath(f"/{bucket}/rename/file.txt").exists()
    assert GCSPath(f"/{bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_rename_files_across_buckets(with_adapter):
    # Rename a single file across buckets
    GCSPath(f"/{bucket}/rename/file.txt").write_text("---")
    GCSPath(f"/{bucket}/rename/file.txt").rename(f"/{other_bucket}/rename/other.txt")
    assert not GCSPath(f"/{bucket}/rename/file.txt").exists()
    assert GCSPath(f"/{other_bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_rename_folders_in_bucket(with_adapter):
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


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_rename_folders_across_buckets(with_adapter):
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


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_replace_files_in_bucket(with_adapter):
    # replace a single file
    GCSPath(f"/{bucket}/replace/file.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/file.txt").replace(f"/{bucket}/replace/other.txt")
    assert not GCSPath(f"/{bucket}/replace/file.txt").exists()
    assert GCSPath(f"/{bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_replace_files_across_buckets(with_adapter):
    # Rename a single file across buckets
    GCSPath(f"/{bucket}/replace/file.txt").write_text("---")
    GCSPath(f"/{bucket}/replace/file.txt").replace(f"/{other_bucket}/replace/other.txt")
    assert not GCSPath(f"/{bucket}/replace/file.txt").exists()
    assert GCSPath(f"/{other_bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_replace_folders_in_bucket(with_adapter):
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


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_replace_folders_across_buckets(with_adapter):
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


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_rmdir(with_adapter):
    GCSPath(f"/{bucket}/rmdir/one.txt").write_text("---")
    GCSPath(f"/{bucket}/rmdir/folder/two.txt").write_text("---")
    path = GCSPath(f"/{bucket}/rmdir/")
    path.rmdir()
    assert not GCSPath(f"/{bucket}/rmdir/one.txt").is_file()
    assert not GCSPath(f"/{bucket}/rmdir/other/two.txt").is_file()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_mkdir(with_adapter):
    bucket_name = f"gcspath-e2e-test-{uuid4().hex}"
    # Create a bucket
    GCSPath(f"/{bucket_name}/").mkdir()
    # Does not assert if it already exists
    GCSPath(f"/{bucket_name}/").mkdir(exist_ok=True)
    with pytest.raises(FileExistsError):
        GCSPath(f"/{bucket_name}/").mkdir(exist_ok=False)
    # with pytest.raises(FileNotFoundError):
    #     GCSPath("/test-second-bucket/test-directory/file.name").mkdir()
    # GCSPath("/test-second-bucket/test-directory/file.name").mkdir(parents=True)
    assert GCSPath(f"/{bucket_name}/").exists()
    # remove the bucket
    # client = storage.Client()
    # bucket = client.lookup_bucket(bucket_name)
    # bucket.delete()
    GCSPath(f"/{bucket_name}/").rmdir()
