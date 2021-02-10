import os
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from uuid import uuid4

import pytest
import spacy

from pathy import (
    BasePath,
    Blob,
    BlobStat,
    Bucket,
    BucketClient,
    BucketClientFS,
    BucketsAccessor,
    FluidPath,
    Pathy,
    PurePathy,
    clear_fs_cache,
    use_fs,
    use_fs_cache,
)
from pathy.about import __version__

from .conftest import TEST_ADAPTERS

# todo: test samefile/touch method
# todo: test open method check R/W bytes/unicode
# todo(jd): replace global test-bucket with mock or generate buckets and call these e2e tests


def test_base_package_declares_version() -> None:
    assert __version__ is not None


def test_base_not_supported(monkeypatch: Any) -> None:
    monkeypatch.setattr(Pathy._flavour, "is_supported", False)
    with pytest.raises(NotImplementedError):
        Pathy()


def test_base_cwd() -> None:
    with pytest.raises(NotImplementedError):
        Pathy.cwd()


def test_base_home() -> None:
    with pytest.raises(NotImplementedError):
        Pathy.home()


def test_base_expanduser() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.expanduser()


def test_base_chmod() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.chmod(0o666)


def test_base_lchmod() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lchmod(0o666)


def test_base_group() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.group()


def test_base_is_mount() -> None:
    assert not Pathy("/fake-bucket/fake-key").is_mount()


def test_base_is_symlink() -> None:
    assert not Pathy("/fake-bucket/fake-key").is_symlink()


def test_base_is_socket() -> None:
    assert not Pathy("/fake-bucket/fake-key").is_socket()


def test_base_is_fifo() -> None:
    assert not Pathy("/fake-bucket/fake-key").is_fifo()


def test_base_is_block_device() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_block_device()


def test_base_is_char_device() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_char_device()


def test_base_lstat() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lstat()


def test_base_symlink_to() -> None:
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.symlink_to("file_name")


def test_base_paths_of_a_different_flavour() -> None:
    with pytest.raises(TypeError):
        PurePathy("/bucket/key") < PurePosixPath("/bucket/key")

    with pytest.raises(TypeError):
        PureWindowsPath("/bucket/key") > PurePathy("/bucket/key")


def test_base_repr() -> None:
    a = PurePathy("/var/tests/fake")
    assert a.as_posix() == "/var/tests/fake"
    assert repr(PurePathy("fake_file.txt")) == "PurePathy('fake_file.txt')"
    assert str(PurePathy("fake_file.txt")) == "fake_file.txt"
    assert bytes(PurePathy("fake_file.txt")) == b"fake_file.txt"


def test_base_scheme_extraction() -> None:
    assert PurePathy("gs://var/tests/fake").scheme == "gs"
    assert PurePathy("s3://var/tests/fake").scheme == "s3"
    assert PurePathy("file://var/tests/fake").scheme == "file"
    assert PurePathy("/var/tests/fake").scheme == ""


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_base_fspath() -> None:
    assert os.fspath(PurePathy("/var/tests/fake")) == "/var/tests/fake"


def test_base_join_strs() -> None:
    assert PurePathy("foo", "some/path", "bar") == PurePathy("foo/some/path/bar")


def test_base_join_paths() -> None:
    assert PurePathy(Path("foo"), Path("bar")) == PurePathy("foo/bar")


def test_base_empty() -> None:
    assert PurePathy() == PurePathy(".")


def test_base_absolute_paths() -> None:
    assert PurePathy("/etc", "/usr", "lib64") == PurePathy("/usr/lib64")


def test_base_slashes_single_double_dots() -> None:
    assert PurePathy("foo//bar") == PurePathy("foo/bar")
    assert PurePathy("foo/./bar") == PurePathy("foo/bar")
    assert PurePathy("foo/../bar") == PurePathy("bar")
    assert PurePathy("../bar") == PurePathy("../bar")
    assert PurePathy("foo", "../bar") == PurePathy("bar")


def test_base_operators() -> None:
    assert PurePathy("/etc") / "init.d" / "apache2" == PurePathy("/etc/init.d/apache2")
    assert "/var" / PurePathy("tests") / "fake" == PurePathy("/var/tests/fake")


def test_base_parts() -> None:
    assert PurePathy("../bar").parts == ("..", "bar")
    assert PurePathy("foo//bar").parts == ("foo", "bar")
    assert PurePathy("foo/./bar").parts == ("foo", "bar")
    assert PurePathy("foo/../bar").parts == ("bar",)
    assert PurePathy("foo", "../bar").parts == ("bar",)
    assert PurePathy("/foo/bar").parts == ("/", "foo", "bar")


def test_base_drive() -> None:
    assert PurePathy("foo//bar").drive == ""
    assert PurePathy("foo/./bar").drive == ""
    assert PurePathy("foo/../bar").drive == ""
    assert PurePathy("../bar").drive == ""
    assert PurePathy("foo", "../bar").drive == ""
    assert PurePathy("/foo/bar").drive == ""


def test_base_root() -> None:
    assert PurePathy("foo//bar").root == ""
    assert PurePathy("foo/./bar").root == ""
    assert PurePathy("foo/../bar").root == ""
    assert PurePathy("../bar").root == ""
    assert PurePathy("foo", "../bar").root == ""
    assert PurePathy("/foo/bar").root == "/"


def test_base_anchor() -> None:
    assert PurePathy("foo//bar").anchor == ""
    assert PurePathy("foo/./bar").anchor == ""
    assert PurePathy("foo/../bar").anchor == ""
    assert PurePathy("../bar").anchor == ""
    assert PurePathy("foo", "../bar").anchor == ""
    assert PurePathy("/foo/bar").anchor == "/"


def test_base_parents() -> None:
    assert tuple(PurePathy("foo//bar").parents) == (
        PurePathy("foo"),
        PurePathy("."),
    )
    assert tuple(PurePathy("foo/./bar").parents) == (
        PurePathy("foo"),
        PurePathy("."),
    )
    assert tuple(PurePathy("foo/../bar").parents) == (PurePathy("."),)
    assert tuple(PurePathy("../bar").parents) == (PurePathy(".."), PurePathy("."))
    assert tuple(PurePathy("foo", "../bar").parents) == (PurePathy("."),)
    assert tuple(PurePathy("/foo/bar").parents) == (
        PurePathy("/foo"),
        PurePathy("/"),
    )


def test_base_parent() -> None:
    assert PurePathy("foo//bar").parent == PurePathy("foo")
    assert PurePathy("foo/./bar").parent == PurePathy("foo")
    assert PurePathy("foo/../bar").parent == PurePathy(".")
    assert PurePathy("../bar").parent == PurePathy("..")
    assert PurePathy("foo", "../bar").parent == PurePathy(".")
    assert PurePathy("/foo/bar").parent == PurePathy("/foo")
    assert PurePathy(".").parent == PurePathy(".")
    assert PurePathy("/").parent == PurePathy("/")


def test_base_name() -> None:
    assert PurePathy("my/library/fake_file.txt").name == "fake_file.txt"


def test_base_suffix() -> None:
    assert PurePathy("my/library/fake_file.txt").suffix == ".txt"
    assert PurePathy("my/library.tar.gz").suffix == ".gz"
    assert PurePathy("my/library").suffix == ""


def test_base_suffixes() -> None:
    assert PurePathy("my/library.tar.gar").suffixes == [".tar", ".gar"]
    assert PurePathy("my/library.tar.gz").suffixes == [".tar", ".gz"]
    assert PurePathy("my/library").suffixes == []


def test_base_stem() -> None:
    assert PurePathy("my/library.tar.gar").stem == "library.tar"
    assert PurePathy("my/library.tar").stem == "library"
    assert PurePathy("my/library").stem == "library"


def test_base_uri() -> None:
    assert PurePathy("/etc/passwd").as_uri() == "gs://etc/passwd"
    assert PurePathy("/etc/init.d/apache2").as_uri() == "gs://etc/init.d/apache2"
    assert PurePathy("/bucket/key").as_uri() == "gs://bucket/key"


def test_base_absolute() -> None:
    assert PurePathy("/a/b").is_absolute()
    assert not PurePathy("a/b").is_absolute()


def test_base_reserved() -> None:
    assert not PurePathy("/a/b").is_reserved()
    assert not PurePathy("a/b").is_reserved()


def test_base_joinpath() -> None:
    assert PurePathy("/etc").joinpath("passwd") == PurePathy("/etc/passwd")
    assert PurePathy("/etc").joinpath(PurePathy("passwd")) == PurePathy("/etc/passwd")
    assert PurePathy("/etc").joinpath("init.d", "apache2") == PurePathy(
        "/etc/init.d/apache2"
    )


def test_base_match() -> None:
    assert PurePathy("a/b.py").match("*.py")
    assert PurePathy("/a/b/c.py").match("b/*.py")
    assert not PurePathy("/a/b/c.py").match("a/*.py")
    assert PurePathy("/a.py").match("/*.py")
    assert not PurePathy("a/b.py").match("/*.py")
    assert not PurePathy("a/b.py").match("*.Py")


def test_base_relative_to() -> None:
    gcs_path = PurePathy("/etc/passwd")
    assert gcs_path.relative_to("/") == PurePathy("etc/passwd")
    assert gcs_path.relative_to("/etc") == PurePathy("passwd")
    with pytest.raises(ValueError):
        gcs_path.relative_to("/usr")


def test_base_with_name() -> None:
    gcs_path = PurePathy("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_name("fake_file.txt") == PurePathy("/Downloads/fake_file.txt")
    gcs_path = PurePathy("/")
    with pytest.raises(ValueError):
        gcs_path.with_name("fake_file.txt")


def test_base_with_suffix() -> None:
    gcs_path = PurePathy("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_suffix(".bz2") == PurePathy("/Downloads/pathlib.tar.bz2")
    gcs_path = PurePathy("README")
    assert gcs_path.with_suffix(".txt") == PurePathy("README.txt")
    gcs_path = PurePathy("README.txt")
    assert gcs_path.with_suffix("") == PurePathy("README")


def test_api_path_support() -> None:
    assert PurePathy in Pathy.mro()  # type: ignore
    assert Path in Pathy.mro()  # type: ignore


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_path_instance(with_adapter: str) -> None:
    blob = Pathy("gs://fake/blob")
    assert isinstance(blob, Path)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_fluid(with_adapter: str, bucket: str) -> None:
    path: FluidPath = Pathy.fluid(f"gs://{bucket}/fake-key")
    assert isinstance(path, Pathy)
    path = Pathy.fluid("foo/bar.txt")
    assert isinstance(path, BasePath)
    path = Pathy.fluid("/dev/null")
    assert isinstance(path, BasePath)


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_path_to_local(with_adapter: str, bucket: str) -> None:
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
def test_api_stat(with_adapter: str, bucket: str) -> None:
    path = Pathy("fake-bucket-1234-0987/fake-key")
    with pytest.raises(ValueError):
        path.stat()
    path = Pathy(f"gs://{bucket}/foo.txt")
    path.write_text("a-a-a-a-a-a-a")
    stat = path.stat()
    assert isinstance(stat, BlobStat)
    assert stat.size is not None and stat.size > 0
    assert stat.last_modified is not None and stat.last_modified > 0
    with pytest.raises(ValueError):
        assert Pathy(f"gs://{bucket}").stat()
    with pytest.raises(FileNotFoundError):
        assert Pathy(f"gs://{bucket}/nonexistant_file.txt").stat()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_resolve(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/fake-key")
    assert path.resolve() == path
    path = Pathy(f"gs://{bucket}/dir/../fake-key")
    assert path.resolve() == Pathy(f"gs://{bucket}/fake-key")


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_exists(with_adapter: str, bucket: str) -> None:
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
def test_api_glob(with_adapter: str, bucket: str) -> None:
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
def test_api_unlink_path(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/unlink/404.txt")
    with pytest.raises(FileNotFoundError):
        path.unlink()
    path = Pathy(f"gs://{bucket}/unlink/foo.txt")
    path.write_text("---")
    assert path.exists()
    path.unlink()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_dir(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/is_dir/subfolder/another/my.file")
    path.write_text("---")
    assert path.is_dir() is False
    for parent in path.parents:
        assert parent.is_dir() is True


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_is_file(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/is_file/subfolder/another/my.file")
    path.write_text("---")
    # The full file is a file
    assert path.is_file() is True
    # Each parent node in the path is only a directory
    for parent in path.parents:
        assert parent.is_file() is False


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_iterdir(with_adapter: str, bucket: str) -> None:
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
def test_api_iterdir_pipstore(with_adapter: str, bucket: str) -> None:
    path = Pathy.from_bucket(bucket) / "iterdir_pipstore/prodigy/prodigy.whl"
    path.write_bytes(b"---")
    path = Pathy.from_bucket(bucket) / "iterdir_pipstore"
    res = [e.name for e in sorted(path.iterdir())]
    assert res == ["prodigy"]


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_for_read(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/read/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_for_write(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/write/file.txt")
    with path.open(mode="w") as file_obj:
        file_obj.write("---")
        file_obj.writelines(["---"])
    path = Pathy(f"gs://{bucket}/write/file.txt")
    with path.open() as file_obj:
        assert file_obj.read() == "------"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_open_binary_read(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/read_binary/file.txt")
    path.write_bytes(b"---")
    with path.open(mode="rb") as file_obj:
        assert file_obj.readlines() == [b"---"]
    with path.open(mode="rb") as file_obj:
        assert file_obj.readline() == b"---"
        assert file_obj.readline() == b""


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_text(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/write_text/file.txt")
    path.write_text("---")
    with path.open() as file_obj:
        assert file_obj.read() == "---"
    assert path.read_text() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_bytes(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/write_bytes/file.txt")
    path.write_bytes(b"---")
    assert path.read_bytes() == b"---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_readwrite_lines(with_adapter: str, bucket: str) -> None:
    path = Pathy(f"gs://{bucket}/write_text/file.txt")
    with path.open("w") as file_obj:
        file_obj.writelines(["---"])
    with path.open("r") as file_obj:
        assert file_obj.readlines() == ["---"]
    with path.open("rt") as file_obj:
        assert file_obj.readline() == "---"


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_ls_blobs_with_stat(with_adapter: str, bucket: str) -> None:
    root = Pathy(f"gs://{bucket}/ls")
    for i in range(3):
        (root / f"file_{i}").write_text("NICE")
    files = list(root.ls())
    assert len(files) == 3
    for i, blob_stat in enumerate(files):
        assert blob_stat.name == f"file_{i}"
        assert blob_stat.size == 4
        assert blob_stat.last_modified is not None


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_owner(with_adapter: str, bucket: str) -> None:
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
    path.owner()
    # dumb assert means we didn't raise
    assert True


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_files_in_bucket(with_adapter: str, bucket: str) -> None:
    # Rename a single file
    Pathy(f"gs://{bucket}/rename/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/file.txt").rename(f"gs://{bucket}/rename/other.txt")
    assert not Pathy(f"gs://{bucket}/rename/file.txt").exists()
    assert Pathy(f"gs://{bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_files_across_buckets(
    with_adapter: str, bucket: str, other_bucket: str
) -> None:
    # Rename a single file across buckets
    Pathy(f"gs://{bucket}/rename/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/rename/file.txt").rename(
        f"gs://{other_bucket}/rename/other.txt"
    )
    assert not Pathy(f"gs://{bucket}/rename/file.txt").exists()
    assert Pathy(f"gs://{other_bucket}/rename/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rename_folders_in_bucket(with_adapter: str, bucket: str) -> None:
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
    with_adapter: str, bucket: str, other_bucket: str
) -> None:
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
def test_api_replace_files_in_bucket(with_adapter: str, bucket: str) -> None:
    # replace a single file
    Pathy(f"gs://{bucket}/replace/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/file.txt").replace(f"gs://{bucket}/replace/other.txt")
    assert not Pathy(f"gs://{bucket}/replace/file.txt").exists()
    assert Pathy(f"gs://{bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_files_across_buckets(
    with_adapter: str, bucket: str, other_bucket: str
) -> None:
    # Rename a single file across buckets
    Pathy(f"gs://{bucket}/replace/file.txt").write_text("---")
    Pathy(f"gs://{bucket}/replace/file.txt").replace(
        f"gs://{other_bucket}/replace/other.txt"
    )
    assert not Pathy(f"gs://{bucket}/replace/file.txt").exists()
    assert Pathy(f"gs://{other_bucket}/replace/other.txt").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_replace_folders_in_bucket(with_adapter: str, bucket: str) -> None:
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
    with_adapter: str, bucket: str, other_bucket: str
) -> None:
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
def test_api_rmdir(with_adapter: str, bucket: str) -> None:
    Pathy(f"gs://{bucket}/rmdir/one.txt").write_text("---")
    Pathy(f"gs://{bucket}/rmdir/folder/two.txt").write_text("---")
    path = Pathy(f"gs://{bucket}/rmdir/")
    path.rmdir()
    assert not Pathy(f"gs://{bucket}/rmdir/one.txt").is_file()
    assert not Pathy(f"gs://{bucket}/rmdir/other/two.txt").is_file()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_rglob_unlink(with_adapter: str, bucket: str) -> None:
    files = [f"gs://{bucket}/rglob_and_unlink/{i}.file.txt" for i in range(3)]
    for file in files:
        Pathy(file).write_text("---")
    path = Pathy(f"gs://{bucket}/rglob_and_unlink/")
    for blob in path.rglob("*"):
        blob.unlink()
    # All the files are gone
    for file in files:
        assert Pathy(file).exists() is False
    # The folder is gone
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_mkdir(with_adapter: str, bucket: str) -> None:
    bucket_name = f"pathy-e2e-test-{uuid4().hex}"
    # Create a bucket
    path = Pathy(f"gs://{bucket_name}/")
    path.mkdir()
    assert path.exists()
    # Does not assert if it already exists
    path.mkdir(exist_ok=True)
    with pytest.raises(FileExistsError):
        path.mkdir(exist_ok=False)
    # with pytest.raises(FileNotFoundError):
    #     Pathy("/test-second-bucket/test-directory/file.name").mkdir()
    # Pathy("/test-second-bucket/test-directory/file.name").mkdir(parents=True)
    assert path.exists()
    # remove the bucket
    # client = storage.Client()
    # bucket = client.lookup_bucket(bucket_name)
    # bucket.delete()
    path.rmdir()
    assert not path.exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_api_ignore_extension(with_adapter: str, bucket: str) -> None:
    """The smart_open library does automatic decompression based
    on the filename. We disable that to avoid errors, e.g. if you
    have a .tar.gz file that isn't gzipped."""
    not_targz = Pathy.from_bucket(bucket) / "ignore_ext/one.tar.gz"
    fixture_tar = Path(__file__).parent / "fixtures" / "tar_but_not_gzipped.tar.gz"
    not_targz.write_bytes(fixture_tar.read_bytes())
    again = not_targz.read_bytes()
    assert again is not None


def test_api_raises_with_no_known_bucket_clients_for_a_scheme(
    temp_folder: Path,
) -> None:
    accessor = BucketsAccessor()
    path = Pathy("foo://foo")
    with pytest.raises(ValueError):
        accessor.client(path)
    # Setting a fallback FS adapter fixes the problem
    use_fs(str(temp_folder))
    assert isinstance(accessor.client(path), BucketClientFS)


@pytest.mark.skip("requires: https://github.com/explosion/thinc/pull/465")
def test_api_export_spacy_model(temp_folder: Path) -> None:
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


def test_client_create_bucket(temp_folder: Path) -> None:
    bucket_target = temp_folder / "foo"
    assert bucket_target.exists() is False
    cl = BucketClientFS(temp_folder)
    cl.create_bucket(PurePathy("gs://foo/"))
    assert bucket_target.exists() is True


def test_client_base_bucket_raises_not_implemented() -> None:
    bucket = Bucket()
    blob: Blob = Blob(bucket, "foo", -1, -1, None, None)
    with pytest.raises(NotImplementedError):
        bucket.copy_blob(blob, bucket, "baz")
    with pytest.raises(NotImplementedError):
        bucket.get_blob("baz")
    with pytest.raises(NotImplementedError):
        bucket.delete_blobs([blob])
    with pytest.raises(NotImplementedError):
        bucket.delete_blob(blob)
    with pytest.raises(NotImplementedError):
        bucket.exists()


def test_client_base_blob_raises_not_implemented() -> None:
    blob: Blob = Blob(Bucket(), "foo", -1, -1, None, None)
    with pytest.raises(NotImplementedError):
        blob.delete()
    with pytest.raises(NotImplementedError):
        blob.exists()


def test_client_base_bucket_client_raises_not_implemented() -> None:
    client = BucketClient()
    with pytest.raises(NotImplementedError):
        client.lookup_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.get_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.list_buckets()
    with pytest.raises(NotImplementedError):
        client.list_blobs(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.scandir(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.create_bucket(Pathy("gs://foo"))
    with pytest.raises(NotImplementedError):
        client.delete_bucket(Pathy("gs://foo"))
