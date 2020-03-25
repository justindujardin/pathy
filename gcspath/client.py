from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

try:
    from google.cloud import storage
except ImportError:
    storage = None

__all__ = (
    "BucketStatResult",
    "BucketDirEntry",
)

BucketStatResult = namedtuple("BucketStatResult", "size, last_modified")


class BucketDirEntry:
    def __init__(self, name, is_dir, size=None, last_modified=None):
        self.name = name
        self._is_dir = is_dir
        self._stat = BucketStatResult(size=size, last_modified=last_modified)

    def __repr__(self):
        return "{}(name={}, is_dir={}, stat={})".format(
            type(self).__name__, self.name, self._is_dir, self._stat
        )

    def inode(self, *args, **kwargs):
        return None

    def is_dir(self):
        return self._is_dir

    def is_file(self):
        return not self._is_dir

    def is_symlink(self, *args, **kwargs):
        return False

    def stat(self):
        return self._stat
