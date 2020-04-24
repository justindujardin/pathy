import pytest
from pathy import Pathy
from pathy.cli import app
from typer.testing import CliRunner


from .conftest import TEST_ADAPTERS

runner = CliRunner()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_cp_file(with_adapter, bucket: str):
    source = f"gs://{bucket}/cli_cp_file/file.txt"
    destination = f"gs://{bucket}/cli_cp_file/other.txt"
    Pathy(source).write_text("---")
    assert runner.invoke(app, ["cp", source, destination]).exit_code == 0
    assert Pathy(source).exists()
    assert Pathy(destination).is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_cp_folder(with_adapter, bucket: str):
    root = Pathy.from_bucket(bucket)
    source = root / "cli_cp_folder"
    destination = root / "cli_cp_folder_other"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")
    assert runner.invoke(app, ["cp", str(source), str(destination)]).exit_code == 0
    assert Pathy(source).exists()
    assert Pathy(destination).is_dir()
    for i in range(2):
        for j in range(2):
            assert (destination / f"{i}" / f"{j}").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_mv_folder(with_adapter, bucket: str):
    root = Pathy.from_bucket(bucket)
    source = root / "cli_mv_folder"
    destination = root / "cli_mv_folder_other"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")
    assert runner.invoke(app, ["mv", str(source), str(destination)]).exit_code == 0
    assert not Pathy(source).exists()
    assert Pathy(destination).is_dir()
    # Ensure source files are gone
    for i in range(2):
        for j in range(2):
            assert not (source / f"{i}" / f"{j}").is_file()
    # And dest files exist
    for i in range(2):
        for j in range(2):
            assert (destination / f"{i}" / f"{j}").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_mv_file(with_adapter, bucket: str):
    source = f"gs://{bucket}/cli_mv_file/file.txt"
    destination = f"gs://{bucket}/cli_mv_file/other.txt"
    Pathy(source).write_text("---")
    assert Pathy(source).exists()
    assert runner.invoke(app, ["mv", source, destination]).exit_code == 0
    assert not Pathy(source).exists()
    assert Pathy(destination).is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_mv_file_across_buckets(with_adapter, bucket: str, other_bucket: str):
    source = f"gs://{bucket}/cli_mv_file_across_buckets/file.txt"
    destination = f"gs://{other_bucket}/cli_mv_file_across_buckets/other.txt"
    Pathy(source).write_text("---")
    assert Pathy(source).exists()
    assert runner.invoke(app, ["mv", source, destination]).exit_code == 0
    assert not Pathy(source).exists()
    assert Pathy(destination).is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_mv_folder_across_buckets(with_adapter, bucket: str, other_bucket: str):
    source = Pathy.from_bucket(bucket) / "cli_mv_folder_across_buckets"
    destination = Pathy.from_bucket(other_bucket) / "cli_mv_folder_across_buckets"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")
    assert runner.invoke(app, ["mv", str(source), str(destination)]).exit_code == 0
    assert not Pathy(source).exists()
    assert Pathy(destination).is_dir()
    # Ensure source files are gone
    for i in range(2):
        for j in range(2):
            assert not (source / f"{i}" / f"{j}").is_file()
    # And dest files exist
    for i in range(2):
        for j in range(2):
            assert (destination / f"{i}" / f"{j}").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_rm_file(with_adapter, bucket: str):
    source = f"gs://{bucket}/cli_rm_file/file.txt"
    Pathy(source).write_text("---")
    assert Pathy(source).exists()
    assert runner.invoke(app, ["rm", source]).exit_code == 0
    assert not Pathy(source).exists()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_rm_verbose(with_adapter, bucket: str):
    root = Pathy.from_bucket(bucket) / "cli_rm_folder"
    source = str(root / "file.txt")
    other = str(root / "folder/other")
    Pathy(source).write_text("---")
    Pathy(other).write_text("---")
    result = runner.invoke(app, ["rm", "-v", source])
    assert result.exit_code == 0
    assert source in result.output
    assert other not in result.output

    Pathy(source).write_text("---")
    result = runner.invoke(app, ["rm", "-rv", str(root)])
    assert result.exit_code == 0
    assert source in result.output
    assert other in result.output


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_rm_folder(with_adapter, bucket: str):
    root = Pathy.from_bucket(bucket)
    source = root / "cli_rm_folder"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")

    # Returns exit code 1 without recursive flag when given a folder
    assert runner.invoke(app, ["rm", str(source)]).exit_code == 1
    assert runner.invoke(app, ["rm", "-r", str(source)]).exit_code == 0
    assert not Pathy(source).exists()
    # Ensure source files are gone
    for i in range(2):
        for j in range(2):
            assert not (source / f"{i}" / f"{j}").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_ls(with_adapter, bucket: str):
    root = Pathy.from_bucket(bucket) / "cli_ls"
    one = str(root / f"file.txt")
    two = str(root / f"other.txt")
    three = str(root / f"folder/file.txt")
    Pathy(one).write_text("---")
    Pathy(two).write_text("---")
    Pathy(three).write_text("---")
    result = runner.invoke(app, ["ls", str(root)])
    assert result.exit_code == 0
    assert one in result.output
    assert two in result.output
    assert str(root / "folder") in result.output
