import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# from gcspath.client import BucketClientFS


@pytest.fixture()
def temp_folder():
    _, tmp_file = tempfile.mkstemp()
    yield Path(tmp_file + os.sep)
    os.remove(tmp_file)


def test_client_create_bucket(temp_folder: Path):
    bucket_target = temp_folder / "foo"
    assert bucket_target.exists() is False
    # cl = BucketClientFS()
    # cl.create_bucket("foo")
    # assert bucket_target.exists() is True
