from pathlib import Path
from time import sleep
from uuid import uuid4

import mock
import pytest
import spacy
from google.auth.exceptions import DefaultCredentialsError

from .conftest import TEST_ADAPTERS

from pathy import (
    BucketClientFS,
    BucketsAccessor,
    BucketStat,
    FluidPath,
    Pathy,
    PureGCSPath,
    clear_fs_cache,
    get_fs_client,
    use_fs,
    use_fs_cache,
)

# todo: test samefile/touch/write_text/write_bytes method
# todo: test security and boto config changes
# todo: test open method check R/W bytes/unicode
# todo(jd): replace global test-bucket with mock or generate buckets and call these e2e tests


def test_api_path_support():
    assert PureGCSPath in Pathy.mro()  # type: ignore
    assert Path in Pathy.mro()  # type: ignore


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_path_instance(with_adapter):
    blob = Pathy("gs://fake/blob")
    assert isinstance(blob, Path)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_fluid(with_adapter, bucket: str):
    path: FluidPath = Pathy.fluid(f"gs://{bucket}/fake-key")
    assert isinstance(path, Pathy)
    path: FluidPath = Pathy.fluid(f"foo/bar.txt")
    assert isinstance(path, Path)
    path: FluidPath = Pathy.fluid(f"/dev/null")
    assert isinstance(path, Path)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_path_to_local(with_adapter, bucket: str):
    root: Pathy = Pathy.from_bucket(bucket) / "to_local"
    foo_blob: Pathy = root / "foo"
    foo_blob.write_text("---")
    assert isinstance(foo_blob, Pathy)
    use_fs_cache()

    # Cache a blob
    cached: Path = Pathy.to_local(foo_blob)
    second_cached: Path = Pathy.to_local(foo_blob)
    assert isinstance(cached, Path)
    assert cached.exists() and cached.is_file(), "local file should exist"
    assert second_cached == cached, "must be the same path"
    assert second_cached.stat() == cached.stat(), "must have the same stat"

    # Cache a folder hierarchy with blobs
    complex_folder = root / "complex"
    for i in range(3):
        folder = f"folder_{i}"
        for j in range(2):
            gcs_blob: Pathy = complex_folder / folder / f"file_{j}.txt"
            gcs_blob.write_text("---")

    cached_folder: Path = Pathy.to_local(complex_folder)
    assert isinstance(cached_folder, Path)
    assert cached_folder.exists() and cached_folder.is_dir()

    # Verify all the files exist in the file-system cache folder
    for i in range(3):
        folder = f"folder_{i}"
        for j in range(2):
            iter_blob: Path = cached_folder / folder / f"file_{j}.txt"
            assert iter_blob.exists()
            assert iter_blob.read_text() == "---"

    clear_fs_cache()
    assert not cached.exists(), "cache clear should delete file"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_use_fs_cache(with_adapter, with_fs: str, bucket: str):
    path = Pathy(f"gs://{bucket}/directory/foo.txt")
    path.write_text("---")
    assert isinstance(path, Pathy)
    with pytest.raises(ValueError):
        Pathy.to_local(path)

    use_fs_cache(with_fs)
    source_file: Path = Pathy.to_local(path)
    foo_timestamp = Path(f"{source_file}.time")
    assert foo_timestamp.exists()
    orig_cache_time = foo_timestamp.read_text()

    # fetch from the local cache
    cached_file: Path = Pathy.to_local(path)
    assert cached_file == source_file
    cached_cache_time = foo_timestamp.read_text()
    assert orig_cache_time == cached_cache_time, "cached blob timestamps should match"

    # Update the blob
    sleep(0.1)
    path.write_text('{ "cool" : true }')

    # Fetch the updated blob
    res: Path = Pathy.to_local(path)
    updated_cache_time = foo_timestamp.read_text()
    assert updated_cache_time != orig_cache_time, "cached timestamp did not change"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_stat(with_adapter, bucket: str):
    path = Pathy("fake-bucket-1234-0987/fake-key")
    with pytest.raises(ValueError):
        path.stat()
    path = Pathy(f"gs://{bucket}/foo.txt")
    path.write_text("a-a-a-a-a-a-a")
    stat = path.stat()
    assert isinstance(stat, BucketStat)
    assert stat.size > 0
    assert stat.last_modified > 0
    with pytest.raises(ValueError):
        assert Pathy(f"gs://{bucket}").stat()
    with pytest.raises(FileNotFoundError):
        assert Pathy(f"gs://{bucket}/nonexistant_file.txt").stat()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_resolve(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/fake-key")
    assert path.resolve() == path
    path = Pathy(f"gs://{bucket}/dir/../fake-key")
    assert path.resolve() == Pathy(f"gs://{bucket}/fake-key")


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_exists(with_adapter, bucket: str):
    path = Pathy("./fake-key")
    with pytest.raises(ValueError):
        path.exists()

    # GCS buckets are globally unique, "test-bucket" exists so this
    # raises an access error.
    assert Pathy("gs://test-bucket/fake-key").exists() is False
    # invalid bucket name
    assert Pathy("gs://unknown-bucket-name-123987519875419").exists() is False
    # valid bucket with invalid object
    assert Pathy(f"gs://{bucket}/not_found_lol_nice.txt").exists() is False

    path = Pathy(f"gs://{bucket}/directory/foo.txt")
    path.write_text("---")
    assert path.exists()
    for parent in path.parents:
        assert parent.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_glob(with_adapter, bucket: str):
    for i in range(3):
        path = Pathy(f"gs://{bucket}/glob/{i}.file")
        path.write_text("---")
    for i in range(2):
        path = Pathy(f"gs://{bucket}/glob/{i}/dir/file.txt")
        path.write_text("---")

    assert list(Pathy(f"gs://{bucket}/glob/").glob("*.test")) == []
    assert sorted(list(Pathy(f"gs://{bucket}/glob/").glob("*.file"))) == [
        Pathy(f"gs://{bucket}/glob/0.file"),
        Pathy(f"gs://{bucket}/glob/1.file"),
        Pathy(f"gs://{bucket}/glob/2.file"),
    ]
    assert list(Pathy(f"gs://{bucket}/glob/0/").glob("*/*.txt")) == [
        Pathy(f"gs://{bucket}/glob/0/dir/file.txt"),
    ]
    assert sorted(Pathy(f"gs://{bucket}").glob("*lob/")) == [
        Pathy(f"gs://{bucket}/glob"),
    ]
    # Recursive matches
    assert sorted(list(Pathy(f"gs://{bucket}/glob/").glob("**/*.txt"))) == [
        Pathy(f"gs://{bucket}/glob/0/dir/file.txt"),
        Pathy(f"gs://{bucket}/glob/1/dir/file.txt"),
    ]
    # rglob adds the **/ for you
    assert sorted(list(Pathy(f"gs://{bucket}/glob/").rglob("*.txt"))) == [
        Pathy(f"gs://{bucket}/glob/0/dir/file.txt"),
        Pathy(f"gs://{bucket}/glob/1/dir/file.txt"),
    ]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_unlink_path(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/unlink/404.txt")
    with pytest.raises(FileNotFoundError):
        path.unlink()
    path = Pathy(f"gs://{bucket}/unlink/foo.txt")
    path.write_text("---")
    assert path.exists()
    path.unlink()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_dir(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/is_dir/subfolder/another/my.file")
    path.write_text("---")
    assert path.is_dir() is False
    for parent in path.parents:
        assert parent.is_dir() is True


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_file(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/is_file/subfolder/another/my.file")
    path.write_text("---")
    # The full file is a file
    assert path.is_file() is True
    # Each parent node in the path is only a directory
    for parent in path.parents:
        assert parent.is_file() is False


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_iterdir(with_adapter, bucket: str):
    # (n) files in a folder
    for i in range(2):
        path = Pathy(f"gs://{bucket}/iterdir/{i}.file")
        path.write_text("---")

    # 1 file in a subfolder
    path = Pathy(f"gs://{bucket}/iterdir/sub/file.txt")
    path.write_text("---")

    path = Pathy(f"gs://{bucket}/iterdir/")
    check = sorted(path.iterdir())
    assert check == [
        Pathy(f"gs://{bucket}/iterdir/0.file"),
        Pathy(f"gs://{bucket}/iterdir/1.file"),
        Pathy(f"gs://{bucket}/iterdir/sub"),
    ]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_iterdir_pipstore(with_adapter, bucket: str):
    path = Pathy.from_bucket(bucket) / "iterdir_pipstore/prodigy/prodigy.whl"
    path.write_bytes(b"---")
    path = Pathy.from_bucket(bucket) / "iterdir_pipstore"
    res = [e.name for e in sorted(path.iterdir())]
    assert res == ["prodigy"]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_for_read(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/read/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_for_write(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/write/file.txt")
    with path.open(mode="w") as file_obj:
        file_obj.write("---")
        file_obj.writelines(["---"])
    path = Pathy(f"gs://{bucket}/write/file.txt")
    with path.open() as file_obj:
        assert file_obj.read() == "------"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_binary_read(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/read_binary/file.txt")
    path.write_bytes(b"---")
    with path.open(mode="rb") as file_obj:
        assert file_obj.readlines() == [b"---"]
    with path.open(mode="rb") as file_obj:
        assert file_obj.readline() == b"---"
        assert file_obj.readline() == b""


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_text(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/write_text/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_bytes(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/write_bytes/file.txt")
    path.write_bytes(b"---")
    assert path.read_bytes() == b"---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_lines(with_adapter, bucket: str):
    path = Pathy(f"gs://{bucket}/write_text/file.txt")
    with path.open("w") as file_obj:
        file_obj.writelines(["---"])
    with path.open("r") as file_obj:
        assert file_obj.readlines() == ["---"]
    with path.open("rt") as file_obj:
        assert file_obj.readline() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_owner(with_adapter, bucket: str):
    # Raises for invalid file
    with pytest.raises(FileNotFoundError):
        Pathy(f"gs://{bucket}/write_text/not_a_valid_blob").owner()

    path = Pathy(f"gs://{bucket}/write_text/file.txt")
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
def test_api_rename_files_in_bucket(with_adapter, bucket: str):
    # Rename a single file
    Pathy(f"gs://{bucket}/rename/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/file.txt").rename(f"gs://{bucket}/rename/other.txt")
    assert not Pathy(f"gs://{bucket}/rename/file.txt").exists()
    assert Pathy(f"gs://{bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_files_across_buckets(with_adapter, bucket: str, other_bucket: str):
    # Rename a single file across buckets
    Pathy(f"gs://{bucket}/rename/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/file.txt").rename(
        f"gs://{other_bucket}/rename/other.txt"
    )
    assert not Pathy(f"gs://{bucket}/rename/file.txt").exists()
    assert Pathy(f"gs://{other_bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_folders_in_bucket(with_adapter, bucket: str):
    # Rename a folder in the same bucket
    Pathy(f"gs://{bucket}/rename/folder/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/rename/folder/")
    new_path = Pathy(f"gs://{bucket}/rename/other/")
    path.rename(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert Pathy(f"gs://{bucket}/rename/other/one.txt").is_file()
    assert Pathy(f"gs://{bucket}/rename/other/two.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_folders_across_buckets(
    with_adapter, bucket: str, other_bucket: str
):
    # Rename a folder across buckets
    Pathy(f"gs://{bucket}/rename/folder/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/rename/folder/")
    new_path = Pathy(f"gs://{other_bucket}/rename/other/")
    path.rename(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert Pathy(f"gs://{other_bucket}/rename/other/one.txt").is_file()
    assert Pathy(f"gs://{other_bucket}/rename/other/two.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_files_in_bucket(with_adapter, bucket: str):
    # replace a single file
    Pathy(f"gs://{bucket}/replace/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/file.txt").replace(
        f"gs://{bucket}/replace/other.txt"
    )
    assert not Pathy(f"gs://{bucket}/replace/file.txt").exists()
    assert Pathy(f"gs://{bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_files_across_buckets(with_adapter, bucket: str, other_bucket: str):
    # Rename a single file across buckets
    Pathy(f"gs://{bucket}/replace/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/file.txt").replace(
        f"gs://{other_bucket}/replace/other.txt"
    )
    assert not Pathy(f"gs://{bucket}/replace/file.txt").exists()
    assert Pathy(f"gs://{other_bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_folders_in_bucket(with_adapter, bucket: str):
    # Rename a folder in the same bucket
    Pathy(f"gs://{bucket}/replace/folder/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/replace/folder/")
    new_path = Pathy(f"gs://{bucket}/replace/other/")
    path.replace(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert Pathy(f"gs://{bucket}/replace/other/one.txt").is_file()
    assert Pathy(f"gs://{bucket}/replace/other/two.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_folders_across_buckets(
    with_adapter, bucket: str, other_bucket: str
):
    # Rename a folder across buckets
    Pathy(f"gs://{bucket}/replace/folder/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/replace/folder/")
    new_path = Pathy(f"gs://{other_bucket}/replace/other/")
    path.replace(new_path)
    assert not path.exists()
    assert new_path.exists()
    assert Pathy(f"gs://{other_bucket}/replace/other/one.txt").is_file()
    assert Pathy(f"gs://{other_bucket}/replace/other/two.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rmdir(with_adapter, bucket: str):
    Pathy(f"gs://{bucket}/rmdir/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/rmdir/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/rmdir/")
    path.rmdir()
    assert not Pathy(f"gs://{bucket}/rmdir/one.txt").is_file()
    assert not Pathy(f"gs://{bucket}/rmdir/other/two.txt").is_file()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_mkdir(with_adapter, bucket: str):
    bucket_name = f"pathy-e2e-test-{uuid4().hex}"
    # Create a bucket
    Pathy(f"gs://{bucket_name}/").mkdir()
    # Does not assert if it already exists
    Pathy(f"gs://{bucket_name}/").mkdir(exist_ok=True)
    with pytest.raises(FileExistsError):
        Pathy(f"gs://{bucket_name}/").mkdir(exist_ok=False)
    # with pytest.raises(FileNotFoundError):
    #     Pathy("/test-second-bucket/test-directory/file.name").mkdir()
    # Pathy("/test-second-bucket/test-directory/file.name").mkdir(parents=True)
    assert Pathy(f"gs://{bucket_name}/").exists()
    # remove the bucket
    # client = storage.Client()
    # bucket = client.lookup_bucket(bucket_name)
    # bucket.delete()
    Pathy(f"gs://{bucket_name}/").rmdir()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_ignore_extension(with_adapter, bucket: str):
    """The smart_open library does automatic decompression based
    on the filename. We disable that to avoid errors, e.g. if you 
    have a .tar.gz file that isn't gzipped."""
    not_targz = Pathy.from_bucket(bucket) / "ignore_ext/one.tar.gz"
    fixture_tar = Path(__file__).parent / "fixtures" / "tar_but_not_gzipped.tar.gz"
    not_targz.write_bytes(fixture_tar.read_bytes())
    again = not_targz.read_bytes()
    assert again is not None


def test_api_use_fs(with_fs: Path):
    assert get_fs_client() is None
    # Use the default path
    use_fs()
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root.exists()

    # Use with False disables the client
    use_fs(False)
    client = get_fs_client()
    assert client is None

    # Can use a given path
    use_fs(str(with_fs))
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root == with_fs

    # Can use a pathlib.Path
    use_fs(with_fs)
    client = get_fs_client()
    assert isinstance(client, BucketClientFS)
    assert client.root == with_fs

    use_fs(False)


@mock.patch("pathy.gcs.BucketClientGCS", side_effect=DefaultCredentialsError())
def test_api_bucket_accessor_without_gcs(bucket_client_gcs_mock, temp_folder):
    accessor = BucketsAccessor()
    # Accessing the client lazily throws with no GCS or FS adapters configured
    with pytest.raises(AssertionError):
        accessor.client

    # Setting a fallback FS adapter fixes the problem
    use_fs(str(temp_folder))
    assert isinstance(accessor.client, BucketClientFS)


def test_api_export_spacy_model(temp_folder):
    """spaCy model loading is one of the things we need to support"""
    use_fs(temp_folder)
    bucket = Pathy("gs://my-bucket/")
    bucket.mkdir(exist_ok=True)
    model = spacy.blank("en")
    output_path = Pathy("gs://my-bucket/models/my_model")
    model.to_disk(output_path)
    sorted_entries = sorted([str(p) for p in output_path.glob("*")])
    expected_entries = [
        "gs://my-bucket/models/my_model/meta.json",
        "gs://my-bucket/models/my_model/tokenizer",
        "gs://my-bucket/models/my_model/vocab",
    ]
    assert sorted_entries == expected_entries
