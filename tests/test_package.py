from pathy.about import __version__


def test_package_defines_version():
    assert isinstance(__version__, str)
