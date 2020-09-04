import pathlib
import shutil
import tempfile
from typing import Any, Dict, Optional, Type, Union

from .base import BucketClient, BucketClientType
from .file import BucketClientFS
from .gcs import BucketClientGCS

# TODO: Maybe this should be dynamic, but I'm trying to see if we can
#       hardcode it (atleast the base schemes) to get nice types flowing
#       in cases where they would otherwise be lost.
_client_registry: Dict[str, Type[BucketClient]] = {
    "file": BucketClientFS,
    "gs": BucketClientGCS,
}

_instance_cache: Dict[str, Any] = {}
_fs_client: Optional[BucketClientFS] = None
_fs_cache: Optional[pathlib.Path] = None


def register_client() -> None:
    """Register a bucket client for use with certain scheme Pathy objects"""
    global _client_registry


def get_client(scheme: str) -> BucketClientType:
    """Retrieve the bucket client for use with a given scheme"""
    global _client_registry, _instance_cache, _fs_client
    if _fs_client is not None:
        return _fs_client  # type: ignore
    if scheme in _instance_cache:
        return _instance_cache[scheme]
    elif scheme in _client_registry:
        _instance_cache[scheme] = _client_registry[scheme]()
        return _instance_cache[scheme]
    raise ValueError(f'There is no client registered to handle "{scheme}" paths')


def use_fs(
    root: Optional[Union[str, pathlib.Path, bool]] = None
) -> Optional[BucketClientFS]:
    """Use a path in the local file-system to store blobs and buckets.

    This is useful for development and testing situations, and for embedded
    applications."""
    global _fs_client
    # False - disable adapter
    if root is False:
        _fs_client = None
        return None

    # None or True - enable FS adapter with default root
    if root is None or root is True:
        # Look up "data" folder of pathy package similar to spaCy
        client_root = pathlib.Path(__file__).parent / "data"
    else:
        assert isinstance(
            root, (str, pathlib.Path)
        ), f"root is not a known type: {type(root)}"
        client_root = pathlib.Path(root)
    if not client_root.exists():
        client_root.mkdir(parents=True)
    _fs_client = BucketClientFS(root=client_root)
    return _fs_client


def get_fs_client() -> Optional[BucketClientFS]:
    """Get the file-system client (or None)"""
    global _fs_client
    assert _fs_client is None or isinstance(
        _fs_client, BucketClientFS
    ), "invalid root type"
    return _fs_client


def use_fs_cache(
    root: Optional[Union[str, pathlib.Path, bool]] = None
) -> Optional[pathlib.Path]:
    """Use a path in the local file-system to cache blobs and buckets.

    This is useful for when you want to avoid fetching large blobs multiple
    times, or need to pass a local file path to a third-party library."""
    global _fs_cache
    # False - disable adapter
    if root is False:
        _fs_cache = None
        return None

    # None or True - enable FS cache with default root
    if root is None or root is True:
        # Use a temporary folder. Cache will be removed according to OS policy
        cache_root = pathlib.Path(tempfile.mkdtemp())
    else:
        assert isinstance(
            root, (str, pathlib.Path)
        ), f"root is not a known type: {type(root)}"
        cache_root = pathlib.Path(root)
    if not cache_root.exists():
        cache_root.mkdir(parents=True)
    _fs_cache = cache_root
    return cache_root


def get_fs_cache() -> Optional[pathlib.Path]:
    """Get the folder that holds file-system cached blobs and timestamps."""
    global _fs_cache
    assert _fs_cache is None or isinstance(_fs_cache, pathlib.Path), "invalid root type"
    return _fs_cache


def clear_fs_cache(force: bool = False) -> None:
    """Remove the existing file-system blob cache folder.

    Raises AssertionError if the cache path is unset or points to the
    root of the file-system."""
    cache_path = get_fs_cache()
    assert cache_path is not None, "no cache to clear"
    resolved = cache_path.resolve()
    assert str(resolved) != "/", f"refusing to remove a root path: {resolved}"
    shutil.rmtree(str(resolved))
