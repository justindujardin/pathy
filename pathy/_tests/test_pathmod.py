from ..pathmod import split, splitdrive, splitext, splitroot


def test_splitdrive_with_scheme() -> None:
    assert splitdrive("gs://bucket/foo") == ("gs", "://bucket/foo")
    assert splitdrive("s3://bucket") == ("s3", "://bucket")


def test_splitdrive_no_scheme() -> None:
    assert splitdrive("foo/bar") == ("", "foo/bar")
    assert splitdrive("") == ("", "")


def test_split_cloud_paths() -> None:
    assert split("gs://bucket/foo/bar") == ("gs://bucket/foo", "bar")
    assert split("gs://bucket/foo") == ("gs://bucket/", "foo")
    assert split("gs://bucket/") == ("gs://bucket/", "")
    assert split("gs://bucket") == ("gs://bucket", "")


def test_split_relative_paths() -> None:
    assert split("foo/bar") == ("foo", "bar")
    assert split("foo") == ("", "foo")
    assert split("") == ("", "")


def test_splitext() -> None:
    assert splitext("foo.tar.gz") == ("foo.tar", ".gz")
    assert splitext("foo") == ("foo", "")


def test_splitroot_with_scheme() -> None:
    assert splitroot("gs://bucket/foo/bar") == ("gs", "bucket", "foo/bar")
    assert splitroot("s3://bucket") == ("s3", "bucket", "")


def test_splitroot_no_scheme() -> None:
    assert splitroot("foo/bar") == ("", "", "foo/bar")
