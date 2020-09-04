import os
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from pathy import Pathy, PurePathy


def test_base_not_supported(monkeypatch):
    monkeypatch.setattr(Pathy._flavour, "is_supported", False)
    with pytest.raises(NotImplementedError):
        Pathy()


def test_base_cwd():
    with pytest.raises(NotImplementedError):
        Pathy.cwd()


def test_base_home():
    with pytest.raises(NotImplementedError):
        Pathy.home()


def test_base_expanduser():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.expanduser()


def test_base_chmod():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.chmod(0o666)


def test_base_lchmod():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lchmod(0o666)


def test_base_group():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.group()


def test_base_is_mount():
    assert not Pathy("/fake-bucket/fake-key").is_mount()


def test_base_is_symlink():
    assert not Pathy("/fake-bucket/fake-key").is_symlink()


def test_base_is_socket():
    assert not Pathy("/fake-bucket/fake-key").is_socket()


def test_base_is_fifo():
    assert not Pathy("/fake-bucket/fake-key").is_fifo()


def test_base_is_block_device():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_block_device()


def test_base_is_char_device():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_char_device()


def test_base_lstat():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lstat()


def test_base_symlink_to():
    path = Pathy("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.symlink_to("file_name")


def test_base_paths_of_a_different_flavour():
    with pytest.raises(TypeError):
        PurePathy("/bucket/key") < PurePosixPath("/bucket/key")

    with pytest.raises(TypeError):
        PureWindowsPath("/bucket/key") > PurePathy("/bucket/key")


def test_base_repr():
    a = PurePathy("/var/tests/fake")
    assert a.as_posix() == "/var/tests/fake"
    assert repr(PurePathy("fake_file.txt")) == "PurePathy('fake_file.txt')"
    assert str(PurePathy("fake_file.txt")) == "fake_file.txt"
    assert bytes(PurePathy("fake_file.txt")) == b"fake_file.txt"


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_base_fspath():
    assert os.fspath(PurePathy("/var/tests/fake")) == "/var/tests/fake"


def test_base_join_strs():
    assert PurePathy("foo", "some/path", "bar") == PurePathy("foo/some/path/bar")


def test_base_join_paths():
    assert PurePathy(Path("foo"), Path("bar")) == PurePathy("foo/bar")


def test_base_empty():
    assert PurePathy() == PurePathy(".")


def test_base_absolute_paths():
    assert PurePathy("/etc", "/usr", "lib64") == PurePathy("/usr/lib64")


def test_base_slashes_single_double_dots():
    assert PurePathy("foo//bar") == PurePathy("foo/bar")
    assert PurePathy("foo/./bar") == PurePathy("foo/bar")
    assert PurePathy("foo/../bar") == PurePathy("bar")
    assert PurePathy("../bar") == PurePathy("../bar")
    assert PurePathy("foo", "../bar") == PurePathy("bar")


def test_base_operators():
    assert PurePathy("/etc") / "init.d" / "apache2" == PurePathy("/etc/init.d/apache2")
    assert "/var" / PurePathy("tests") / "fake" == PurePathy("/var/tests/fake")


def test_base_parts():
    assert PurePathy("../bar").parts == ("..", "bar")
    assert PurePathy("foo//bar").parts == ("foo", "bar")
    assert PurePathy("foo/./bar").parts == ("foo", "bar")
    assert PurePathy("foo/../bar").parts == ("bar",)
    assert PurePathy("foo", "../bar").parts == ("bar",)
    assert PurePathy("/foo/bar").parts == ("/", "foo", "bar")


def test_base_drive():
    assert PurePathy("foo//bar").drive == ""
    assert PurePathy("foo/./bar").drive == ""
    assert PurePathy("foo/../bar").drive == ""
    assert PurePathy("../bar").drive == ""
    assert PurePathy("foo", "../bar").drive == ""
    assert PurePathy("/foo/bar").drive == ""


def test_base_root():
    assert PurePathy("foo//bar").root == ""
    assert PurePathy("foo/./bar").root == ""
    assert PurePathy("foo/../bar").root == ""
    assert PurePathy("../bar").root == ""
    assert PurePathy("foo", "../bar").root == ""
    assert PurePathy("/foo/bar").root == "/"


def test_base_anchor():
    assert PurePathy("foo//bar").anchor == ""
    assert PurePathy("foo/./bar").anchor == ""
    assert PurePathy("foo/../bar").anchor == ""
    assert PurePathy("../bar").anchor == ""
    assert PurePathy("foo", "../bar").anchor == ""
    assert PurePathy("/foo/bar").anchor == "/"


def test_base_parents():
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


def test_base_parent():
    assert PurePathy("foo//bar").parent == PurePathy("foo")
    assert PurePathy("foo/./bar").parent == PurePathy("foo")
    assert PurePathy("foo/../bar").parent == PurePathy(".")
    assert PurePathy("../bar").parent == PurePathy("..")
    assert PurePathy("foo", "../bar").parent == PurePathy(".")
    assert PurePathy("/foo/bar").parent == PurePathy("/foo")
    assert PurePathy(".").parent == PurePathy(".")
    assert PurePathy("/").parent == PurePathy("/")


def test_base_name():
    assert PurePathy("my/library/fake_file.txt").name == "fake_file.txt"


def test_base_suffix():
    assert PurePathy("my/library/fake_file.txt").suffix == ".txt"
    assert PurePathy("my/library.tar.gz").suffix == ".gz"
    assert PurePathy("my/library").suffix == ""


def test_base_suffixes():
    assert PurePathy("my/library.tar.gar").suffixes == [".tar", ".gar"]
    assert PurePathy("my/library.tar.gz").suffixes == [".tar", ".gz"]
    assert PurePathy("my/library").suffixes == []


def test_base_stem():
    assert PurePathy("my/library.tar.gar").stem == "library.tar"
    assert PurePathy("my/library.tar").stem == "library"
    assert PurePathy("my/library").stem == "library"


def test_base_uri():
    assert PurePathy("/etc/passwd").as_uri() == "gs://etc/passwd"
    assert PurePathy("/etc/init.d/apache2").as_uri() == "gs://etc/init.d/apache2"
    assert PurePathy("/bucket/key").as_uri() == "gs://bucket/key"


def test_base_absolute():
    assert PurePathy("/a/b").is_absolute()
    assert not PurePathy("a/b").is_absolute()


def test_base_reserved():
    assert not PurePathy("/a/b").is_reserved()
    assert not PurePathy("a/b").is_reserved()


def test_base_joinpath():
    assert PurePathy("/etc").joinpath("passwd") == PurePathy("/etc/passwd")
    assert PurePathy("/etc").joinpath(PurePathy("passwd")) == PurePathy("/etc/passwd")
    assert PurePathy("/etc").joinpath("init.d", "apache2") == PurePathy(
        "/etc/init.d/apache2"
    )


def test_base_match():
    assert PurePathy("a/b.py").match("*.py")
    assert PurePathy("/a/b/c.py").match("b/*.py")
    assert not PurePathy("/a/b/c.py").match("a/*.py")
    assert PurePathy("/a.py").match("/*.py")
    assert not PurePathy("a/b.py").match("/*.py")
    assert not PurePathy("a/b.py").match("*.Py")


def test_base_relative_to():
    gcs_path = PurePathy("/etc/passwd")
    assert gcs_path.relative_to("/") == PurePathy("etc/passwd")
    assert gcs_path.relative_to("/etc") == PurePathy("passwd")
    with pytest.raises(ValueError):
        gcs_path.relative_to("/usr")


def test_base_with_name():
    gcs_path = PurePathy("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_name("fake_file.txt") == PurePathy("/Downloads/fake_file.txt")
    gcs_path = PurePathy("/")
    with pytest.raises(ValueError):
        gcs_path.with_name("fake_file.txt")


def test_base_with_suffix():
    gcs_path = PurePathy("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_suffix(".bz2") == PurePathy("/Downloads/pathlib.tar.bz2")
    gcs_path = PurePathy("README")
    assert gcs_path.with_suffix(".txt") == PurePathy("README.txt")
    gcs_path = PurePathy("README.txt")
    assert gcs_path.with_suffix("") == PurePathy("README")
