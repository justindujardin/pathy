import pytest
from gcspath import GCSPath
from gcspath.cli import app
from typer.testing import CliRunner


from .conftest import TEST_ADAPTERS

runner = CliRunner()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cp_files(with_adapter):
    source = "gs://gcspath-tests-1/cli_cp.txt"
    destination = "gs://gcspath-tests-2/cli_cp.txt"
    content = "hi"
    dest_path = GCSPath(destination)
    source_path = GCSPath(source)
    source_path.write_text(content)
    assert runner.invoke(app, ["cp", source, destination]).exit_code == 0
    assert dest_path.is_file()
    # Both files exist
    assert source_path.read_text() == content
    assert dest_path.read_text() == content


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cp_folders(with_adapter):
    source = "gs://gcspath-tests-1/cli_cp.txt"
    destination = "gs://gcspath-tests-2/cli_cp.txt"
    content = "hi"
    dest_path = GCSPath(destination)
    source_path = GCSPath(source)
    source_path.write_text(content)
    assert runner.invoke(app, ["cp", source, destination]).exit_code == 0
    assert dest_path.is_file()
    # Both files exist
    assert source_path.read_text() == content
    assert dest_path.read_text() == content
