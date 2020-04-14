import os
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from gcspath import GCSPath, PureGCSPath


def test_not_supported(monkeypatch):
    monkeypatch.setattr(GCSPath._flavour, "is_supported", False)
    with pytest.raises(NotImplementedError):
        GCSPath()


def test_cwd():
    with pytest.raises(NotImplementedError):
        GCSPath.cwd()


def test_home():
    with pytest.raises(NotImplementedError):
        GCSPath.home()


def test_chmod():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.chmod(0o666)


def test_lchmod():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lchmod(0o666)


def test_group():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.group()


def test_is_mount():
    assert not GCSPath("/fake-bucket/fake-key").is_mount()


def test_is_symlink():
    assert not GCSPath("/fake-bucket/fake-key").is_symlink()


def test_is_socket():
    assert not GCSPath("/fake-bucket/fake-key").is_socket()


def test_is_fifo():
    assert not GCSPath("/fake-bucket/fake-key").is_fifo()


def test_is_block_device():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_block_device()


def test_is_char_device():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.is_char_device()


def test_lstat():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.lstat()


def test_symlink_to():
    path = GCSPath("/fake-bucket/fake-key")
    with pytest.raises(NotImplementedError):
        path.symlink_to("file_name")


def test_paths_of_a_different_flavour():
    with pytest.raises(TypeError):
        PureGCSPath("/bucket/key") < PurePosixPath("/bucket/key")

    with pytest.raises(TypeError):
        PureWindowsPath("/bucket/key") > PureGCSPath("/bucket/key")


def test_repr():
    assert repr(PureGCSPath("setup.py")) == "PureGCSPath('setup.py')"
    assert str(PureGCSPath("setup.py")) == "setup.py"
    assert bytes(PureGCSPath("setup.py")) == b"setup.py"
    assert PureGCSPath("/usr/bin").as_posix() == "/usr/bin"


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_fspath():
    assert os.fspath(PureGCSPath("/usr/bin")) == "/usr/bin"


def test_join_strs():
    assert PureGCSPath("foo", "some/path", "bar") == PureGCSPath("foo/some/path/bar")


def test_join_paths():
    assert PureGCSPath(Path("foo"), Path("bar")) == PureGCSPath("foo/bar")


def test_empty():
    assert PureGCSPath() == PureGCSPath(".")


def test_absolute_paths():
    assert PureGCSPath("/etc", "/usr", "lib64") == PureGCSPath("/usr/lib64")


def test_slashes_single_double_dots():
    assert PureGCSPath("foo//bar") == PureGCSPath("foo/bar")
    assert PureGCSPath("foo/./bar") == PureGCSPath("foo/bar")
    assert PureGCSPath("foo/../bar") == PureGCSPath("bar")
    assert PureGCSPath("../bar") == PureGCSPath("../bar")
    assert PureGCSPath("foo", "../bar") == PureGCSPath("bar")


def test_operators():
    assert PureGCSPath("/etc") / "init.d" / "apache2" == PureGCSPath(
        "/etc/init.d/apache2"
    )
    assert "/usr" / PureGCSPath("bin") == PureGCSPath("/usr/bin")


def test_parts():
    assert PureGCSPath("foo//bar").parts == ("foo", "bar")
    assert PureGCSPath("foo/./bar").parts == ("foo", "bar")
    assert PureGCSPath("foo/../bar").parts == ("bar",)
    assert PureGCSPath("../bar").parts == ("..", "bar")
    assert PureGCSPath("foo", "../bar").parts == ("bar",)
    assert PureGCSPath("/foo/bar").parts == ("/", "foo", "bar")


def test_drive():
    assert PureGCSPath("foo//bar").drive == ""
    assert PureGCSPath("foo/./bar").drive == ""
    assert PureGCSPath("foo/../bar").drive == ""
    assert PureGCSPath("../bar").drive == ""
    assert PureGCSPath("foo", "../bar").drive == ""
    assert PureGCSPath("/foo/bar").drive == ""


def test_root():
    assert PureGCSPath("foo//bar").root == ""
    assert PureGCSPath("foo/./bar").root == ""
    assert PureGCSPath("foo/../bar").root == ""
    assert PureGCSPath("../bar").root == ""
    assert PureGCSPath("foo", "../bar").root == ""
    assert PureGCSPath("/foo/bar").root == "/"


def test_anchor():
    assert PureGCSPath("foo//bar").anchor == ""
    assert PureGCSPath("foo/./bar").anchor == ""
    assert PureGCSPath("foo/../bar").anchor == ""
    assert PureGCSPath("../bar").anchor == ""
    assert PureGCSPath("foo", "../bar").anchor == ""
    assert PureGCSPath("/foo/bar").anchor == "/"


def test_parents():
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


def test_parent():
    assert PureGCSPath("foo//bar").parent == PureGCSPath("foo")
    assert PureGCSPath("foo/./bar").parent == PureGCSPath("foo")
    assert PureGCSPath("foo/../bar").parent == PureGCSPath(".")
    assert PureGCSPath("../bar").parent == PureGCSPath("..")
    assert PureGCSPath("foo", "../bar").parent == PureGCSPath(".")
    assert PureGCSPath("/foo/bar").parent == PureGCSPath("/foo")
    assert PureGCSPath(".").parent == PureGCSPath(".")
    assert PureGCSPath("/").parent == PureGCSPath("/")


def test_name():
    assert PureGCSPath("my/library/setup.py").name == "setup.py"


def test_suffix():
    assert PureGCSPath("my/library/setup.py").suffix == ".py"
    assert PureGCSPath("my/library.tar.gz").suffix == ".gz"
    assert PureGCSPath("my/library").suffix == ""


def test_suffixes():
    assert PureGCSPath("my/library.tar.gar").suffixes == [".tar", ".gar"]
    assert PureGCSPath("my/library.tar.gz").suffixes == [".tar", ".gz"]
    assert PureGCSPath("my/library").suffixes == []


def test_stem():
    assert PureGCSPath("my/library.tar.gar").stem == "library.tar"
    assert PureGCSPath("my/library.tar").stem == "library"
    assert PureGCSPath("my/library").stem == "library"


def test_uri():
    assert PureGCSPath("/etc/passwd").as_uri() == "gs://etc/passwd"
    assert PureGCSPath("/etc/init.d/apache2").as_uri() == "gs://etc/init.d/apache2"
    assert PureGCSPath("/bucket/key").as_uri() == "gs://bucket/key"


def test_absolute():
    assert PureGCSPath("/a/b").is_absolute()
    assert not PureGCSPath("a/b").is_absolute()


def test_reserved():
    assert not PureGCSPath("/a/b").is_reserved()
    assert not PureGCSPath("a/b").is_reserved()


def test_joinpath():
    assert PureGCSPath("/etc").joinpath("passwd") == PureGCSPath("/etc/passwd")
    assert PureGCSPath("/etc").joinpath(PureGCSPath("passwd")) == PureGCSPath(
        "/etc/passwd"
    )
    assert PureGCSPath("/etc").joinpath("init.d", "apache2") == PureGCSPath(
        "/etc/init.d/apache2"
    )


def test_match():
    assert PureGCSPath("a/b.py").match("*.py")
    assert PureGCSPath("/a/b/c.py").match("b/*.py")
    assert not PureGCSPath("/a/b/c.py").match("a/*.py")
    assert PureGCSPath("/a.py").match("/*.py")
    assert not PureGCSPath("a/b.py").match("/*.py")
    assert not PureGCSPath("a/b.py").match("*.Py")


def test_relative_to():
    gcs_path = PureGCSPath("/etc/passwd")
    assert gcs_path.relative_to("/") == PureGCSPath("etc/passwd")
    assert gcs_path.relative_to("/etc") == PureGCSPath("passwd")
    with pytest.raises(ValueError):
        gcs_path.relative_to("/usr")


def test_with_name():
    gcs_path = PureGCSPath("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_name("setup.py") == PureGCSPath("/Downloads/setup.py")
    gcs_path = PureGCSPath("/")
    with pytest.raises(ValueError):
        gcs_path.with_name("setup.py")


def test_with_suffix():
    gcs_path = PureGCSPath("/Downloads/pathlib.tar.gz")
    assert gcs_path.with_suffix(".bz2") == PureGCSPath("/Downloads/pathlib.tar.bz2")
    gcs_path = PureGCSPath("README")
    assert gcs_path.with_suffix(".txt") == PureGCSPath("README.txt")
    gcs_path = PureGCSPath("README.txt")
    assert gcs_path.with_suffix("") == PureGCSPath("README")
