import os
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from pathy import Pathy, PureGCSPath


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
        PureGCSPath("/bucket/key") < PurePosixPath("/bucket/key")

    with pytest.raises(TypeError):
        PureWindowsPath("/bucket/key") > PureGCSPath("/bucket/key")


def test_base_repr():
    a = PureGCSPath("/var/tests/fake")
    f = a.prefix
    assert a.as_posix() == "/var/tests/fake"
    assert repr(PureGCSPath("fake_file.txt")) == "PureGCSPath('fake_file.txt')"
    assert str(PureGCSPath("fake_file.txt")) == "fake_file.txt"
    assert bytes(PureGCSPath("fake_file.txt")) == b"fake_file.txt"


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_base_fspath():
    assert os.fspath(PureGCSPath("/var/tests/fake")) == "/var/tests/fake"


def test_base_join_strs():
    assert PureGCSPath("foo", "some/path", "bar") == PureGCSPath("foo/some/path/bar")


def test_base_join_paths():
    assert PureGCSPath(Path("foo"), Path("bar")) == PureGCSPath("foo/bar")


def test_base_empty():
    assert PureGCSPath() == PureGCSPath(".")


def test_base_absolute_paths():
    assert PureGCSPath("/etc", "/usr", "lib64") == PureGCSPath("/usr/lib64")


def test_base_slashes_single_double_dots():
    assert PureGCSPath("foo//bar") == PureGCSPath("foo/bar")
    assert PureGCSPath("foo/./bar") == PureGCSPath("foo/bar")
    assert PureGCSPath("foo/../bar") == PureGCSPath("bar")
    assert PureGCSPath("../bar") == PureGCSPath("../bar")
    assert PureGCSPath("foo", "../bar") == PureGCSPath("bar")


def test_base_operators():
    assert PureGCSPath("/etc") / "init.d" / "apache2" == PureGCSPath(
        "/etc/init.d/apache2"
    )
    assert "/var" / PureGCSPath("tests") / "fake" == PureGCSPath("/var/tests/fake")


def test_base_parts():
    assert PureGCSPath("../bar").parts == ("..", "bar")
    assert PureGCSPath("foo//bar").parts == ("foo", "bar")
    assert PureGCSPath("foo/./bar").parts == ("foo", "bar")
    assert PureGCSPath("foo/../bar").parts == ("bar",)
    assert PureGCSPath("foo", "../bar").parts == ("bar",)
    assert PureGCSPath("/foo/bar").parts == ("/", "foo", "bar")


def test_base_drive():
    assert PureGCSPath("foo//bar").drive == ""
    assert PureGCSPath("foo/./bar").drive == ""
    assert PureGCSPath("foo/../bar").drive == ""
    assert PureGCSPath("../bar").drive == ""
    assert PureGCSPath("foo", "../bar").drive == ""
    assert PureGCSPath("/foo/bar").drive == ""


def test_base_root():
    assert PureGCSPath("foo//bar").root == ""
    assert PureGCSPath("foo/./bar").root == ""
    assert PureGCSPath("foo/../bar").root == ""
    assert PureGCSPath("../bar").root == ""
    assert PureGCSPath("foo", "../bar").root == ""
    assert PureGCSPath("/foo/bar").root == "/"


def test_base_anchor():
    assert PureGCSPath("foo//bar").anchor == ""
    assert PureGCSPath("foo/./bar").anchor == ""
    assert PureGCSPath("foo/../bar").anchor == ""
    assert PureGCSPath("../bar").anchor == ""
    assert PureGCSPath("foo", "../bar").anchor == ""
    assert PureGCSPath("/foo/bar").anchor == "/"


def test_base_parents():
    assert tuple(PureGCSPath("foo//bar").parents) == (
        PureGCSPath("foo"),
        PureGCSPath("."),
    )
    assert tuple(PureGCSPath("foo/./bar").parents) == (
        PureGCSPath("foo"),
        PureGCSPath("."),
    )
    assert tuple(PureGCSPath("foo/../bar").parents) == (PureGCSPath("."),)
    assert tuple(PureGCSPath("../bar").parents) == (PureGCSPath(".."), PureGCSPath("."))
    assert tuple(PureGCSPath("foo", "../bar").parents) == (PureGCSPath("."),)
    assert tuple(PureGCSPath("/foo/bar").parents) == (
        PureGCSPath("/foo"),
        PureGCSPath("/"),
    )


def test_base_parent():
    assert PureGCSPath("foo//bar").parent == PureGCSPath("foo")
    assert PureGCSPath("foo/./bar").parent == PureGCSPath("foo")
    assert PureGCSPath("foo/../bar").parent == PureGCSPath(".")
    assert PureGCSPath("../bar").parent == PureGCSPath("..")
    assert PureGCSPath("foo", "../bar").parent == PureGCSPath(".")
    assert PureGCSPath("/foo/bar").parent == PureGCSPath("/foo")
    assert PureGCSPath(".").parent == PureGCSPath(".")
    assert PureGCSPath("/").parent == PureGCSPath("/")


def test_base_name():
    assert PureGCSPath("my/library/fake_file.txt").name == "fake_file.txt"


def test_base_suffix():
    assert PureGCSPath("my/library/fake_file.txt").suffix == ".txt"
    assert PureGCSPath("my/library.tar.gz").suffix == ".gz"
    assert PureGCSPath("my/library").suffix == ""


def test_base_suffixes():
    assert PureGCSPath("my/library.tar.gar").suffixes == [".tar", ".gar"]
    assert PureGCSPath("my/library.tar.gz").suffixes == [".tar", ".gz"]
    assert PureGCSPath("my/library").suffixes == []


def test_base_stem():
    assert PureGCSPath("my/library.tar.gar").stem == "library.tar"
    assert PureGCSPath("my/library.tar").stem == "library"
    assert PureGCSPath("my/library").stem == "library"


def test_base_uri():
    assert PureGCSPath("/etc/passwd").as_uri() == "gs://etc/passwd"
    assert PureGCSPath("/etc/init.d/apache2").as_uri() == "gs://etc/init.d/apache2"
    assert PureGCSPath("/bucket/key").as_uri() == "gs://bucket/key"


def test_base_absolute():
    assert PureGCSPath("/a/b").is_absolute()
    assert not PureGCSPath("a/b").is_absolute()


def test_base_reserved():
    assert not PureGCSPath("/a/b").is_reserved()
    assert not PureGCSPath("a/b").is_reserved()


def test_base_joinpath():
    assert PureGCSPath("/etc").joinpath("passwd") == PureGCSPath("/etc/passwd")
    assert PureGCSPath("/etc").joinpath(PureGCSPath("passwd")) == PureGCSPath(
        "/etc/passwd"
    )
    assert PureGCSPath("/etc").joinpath("init.d", "apache2") == PureGCSPath(
        "/etc/init.d/apache2"
    )


def test_base_match():
    assert PureGCSPath("a/b.py").match("*.py")
    assert PureGCSPath("/a/b/c.py").match("b/*.py")
    assert not PureGCSPath("/a/b/c.py").match("a/*.py")
    assert PureGCSPath("/a.py").match("/*.py")
    assert not PureGCSPath("a/b.py").match("/*.py")
    assert not PureGCSPath("a/b.py").match("*.Py")


def test_base_relative_to():
    gcs_path = PureGCSPath("/etc/passwd")
    assert gcs_path.relative_to("/") == PureGCSPath("etc/passwd")
    assert gcs_path.relative_to("/etc") == PureGCSPath("passwd")
    with pytest.raises(ValueError):
        gcs_path.relative_to("/usr")


def test_base_with_name():
    gcs_path = PureGCSPath("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_name("fake_file.txt") == PureGCSPath(
        "/Downloads/fake_file.txt"
    )
    gcs_path = PureGCSPath("/")
    with pytest.raises(ValueError):
        gcs_path.with_name("fake_file.txt")


def test_base_with_suffix():
    gcs_path = PureGCSPath("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_suffix(".bz2") == PureGCSPath("/Downloads/pathlib.tar.bz2")
    gcs_path = PureGCSPath("README")
    assert gcs_path.with_suffix(".txt") == PureGCSPath("README.txt")
    gcs_path = PureGCSPath("README.txt")
    assert gcs_path.with_suffix("") == PureGCSPath("README")
