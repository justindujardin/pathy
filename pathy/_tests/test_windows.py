import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from pathy import Pathy, PurePathy

is_windows = os.name == "nt"


@pytest.mark.skipif(not is_windows, reason="requires windows")
def test_windows_fluid_absolute_paths() -> None:
    # Path with \\ slashes
    tmp_dir = tempfile.mkdtemp()
    # Converted to the same path with / slashes
    alt_slashes = tmp_dir.replace("\\\\", "/").replace("\\", "/")

    # Make a folder from \\ absolute path
    fs_root = Pathy.fluid(tmp_dir)
    assert "\\" in str(fs_root), "expected \\ separators in windows path"
    new_folder = Pathy.fluid(fs_root / "sub-dir")
    assert new_folder.exists() is False
    new_folder.mkdir()
    assert new_folder.exists() is True

    # Make a folder from / absolute path
    fs_root = Pathy.fluid(alt_slashes)
    new_folder = Pathy.fluid(fs_root / "sub-dir-alt")
    assert new_folder.exists() is False
    new_folder.mkdir()
    assert new_folder.exists() is True

    shutil.rmtree(tmp_dir)


@pytest.mark.skipif(not is_windows, reason="requires windows")
def test_windows_fluid_absolute_file_paths() -> None:
    # Path with \\ slashes
    tmp_dir = tempfile.mkdtemp()
    # Converted to the same path with / slashes
    alt_slashes = tmp_dir.replace("\\\\", "/").replace("\\", "/")

    # Make a folder from \\ absolute path
    fs_root = Pathy.fluid(f"file://{tmp_dir}")
    assert "\\" in str(fs_root), "expected \\ separators in windows path"
    new_folder = Pathy.fluid(fs_root / "sub-dir")
    assert new_folder.exists() is False
    new_folder.mkdir()
    assert new_folder.exists() is True

    # Make a folder from / absolute path
    fs_root = Pathy.fluid(f"file://{alt_slashes}")
    new_folder = Pathy.fluid(fs_root / "sub-dir-alt/")
    assert new_folder.exists() is False
    new_folder.mkdir()
    assert new_folder.exists() is True

    shutil.rmtree(tmp_dir)


@patch("pathy.os.name", "nt")
def test_format_parsed_parts_windows_join() -> None:
    """Verify file:// paths use backslash joins when os.name is 'nt'."""
    result = PurePathy._format_parsed_parts("file", "/", ["tmp", "sub"])
    assert "\\" in result
