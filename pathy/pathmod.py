import os
import posixpath
from typing import Tuple

sep = "/"
schemesep = "://"

join = posixpath.join
normcase = posixpath.normcase


def isabs(s: str) -> bool:
    """Test whether a path is absolute (has a scheme://)."""
    s = os.fspath(s)
    return schemesep in s


def splitdrive(path: str) -> Tuple[str, str]:
    """Split a cloud path into drive (scheme) and tail.

    splitdrive('gs://bucket/foo') == ('gs', '://bucket/foo')
    splitdrive('://bucket/foo') == ('', '://bucket/foo')
    splitdrive('foo/bar') == ('', 'foo/bar')
    """
    idx = path.find(schemesep)
    if idx == -1:
        return ("", path)
    return (path[:idx], path[idx:])


def split(path: str) -> Tuple[str, str]:
    """Split a cloud path into (head, tail) where tail is the last component.

    The key contract: repeatedly calling split() decomposes until head == path.

    split('gs://bucket/foo/bar') == ('gs://bucket/foo', 'bar')
    split('gs://bucket/foo') == ('gs://bucket/', 'foo')
    split('gs://bucket/') == ('gs://bucket/', '')
    split('gs://bucket') == ('gs://bucket', '')
    split('foo/bar') == ('foo', 'bar')
    split('foo') == ('', 'foo')
    split('') == ('', '')
    """
    if not path:
        return ("", "")

    # Find the scheme separator
    scheme_idx = path.find(schemesep)
    if scheme_idx == -1:
        # No scheme — delegate to posixpath for relative paths
        return posixpath.split(path)

    # Everything after scheme:// is the "rest"
    prefix = path[: scheme_idx + len(schemesep)]  # e.g. "gs://"
    rest = path[scheme_idx + len(schemesep) :]  # e.g. "bucket/foo/bar"

    # Strip trailing slashes from rest for splitting, but remember if there was one
    rest_stripped = rest.rstrip(sep)

    if sep not in rest_stripped:
        # We're at scheme://bucket or scheme://bucket/
        # This is the anchor — return (path, "") to signal fixed point
        return (path, "")

    # Split the last component
    head, tail = rest_stripped.rsplit(sep, 1)

    # Reconstruct: prefix + head, but ensure at least scheme://bucket/
    result_head = prefix + head
    # If head is just the bucket name (no slashes), add trailing slash
    if sep not in head:
        result_head += sep

    return (result_head, tail)


def splitext(path: str) -> Tuple[str, str]:
    """Split the extension from a pathname.

    splitext('foo.tar.gz') == ('foo.tar', '.gz')
    splitext('foo') == ('foo', '')
    """
    return posixpath.splitext(path)


def splitroot(input_path: str, resolve: bool = False) -> Tuple[str, str, str]:
    """Split a pathname into scheme, bucket, and path. For cloud storage all three
    are required. The scheme is one Pathy's supported scehemes, e.g. 'gs', 's3', etc.

        splitroot('gs://bucket/foo/bar') == ('gs', 'bucket', 'foo/bar')
        splitroot('s3://bucket3/bar') == ('s3', 'bucket3', 'bar')
        splitroot('azure://cool/foo/bar') == ('azure', 'cool', 'foo/bar')
    """
    p = os.fspath(input_path)
    empty = ""

    scheme_tail = p.split(schemesep, 1)
    if len(scheme_tail) == 1:
        return empty, empty, p

    scheme, tail = scheme_tail
    parts = tail.split(sep)
    if resolve:
        # Remove any .. parts
        for part in parts[1:]:
            if part == "..":
                index = parts.index(part)
                parts.pop(index - 1)
                parts.remove(part)
    bucket = parts[0]
    path = sep.join(parts[1:]) if len(parts) > 1 else empty
    return scheme, bucket, path
