import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from gcspath import PureGCSPath
from gcspath.file import BucketClientFS, ClientBlobFS, ClientBucketFS


@pytest.fixture()
def temp_folder():
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    shutil.rmtree(tmp_dir)


def test_client_create_bucket(temp_folder: Path):
    bucket_target = temp_folder / "foo"
    assert bucket_target.exists() is False
    cl = BucketClientFS(temp_folder)
    cl.create_bucket(PureGCSPath("/foo/"))
    assert bucket_target.exists() is True
