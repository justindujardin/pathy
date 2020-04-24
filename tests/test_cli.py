import pytest
from gcspath import GCSPath
from gcspath.cli import app
from typer.testing import CliRunner


from .conftest import TEST_ADAPTERS

runner = CliRunner()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_cp_file(with_adapter, bucket: str):
    source = f"gs://{bucket}/cli_cp_file/file.txt"
    destination = f"gs://{bucket}/cli_cp_file/other.txt"
    GCSPath(source).write_text("---")
    assert runner.invoke(app, ["cp", source, destination]).exit_code == 0
    assert GCSPath(source).exists()
    assert GCSPath(destination).is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_cp_folder(with_adapter, bucket: str):
    root = GCSPath.from_bucket(bucket)
    source = root / "cli_cp_folder"
    destination = root / "cli_cp_folder_other"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")
    assert runner.invoke(app, ["cp", str(source), str(destination)]).exit_code == 0
    assert GCSPath(source).exists()
    assert GCSPath(destination).is_dir()
    for i in range(2):
        for j in range(2):
            assert (destination / f"{i}" / f"{j}").is_file()


@pytest.mark.parametrize("adapter", TEST_ADAPTERS)
def test_cli_mv_folder(with_adapter, bucket: str):
    root = GCSPath.from_bucket(bucket)
    source = root / "cli_mv_folder"
    destination = root / "cli_mv_folder_other"
    for i in range(2):
        for j in range(2):
            (source / f"{i}" / f"{j}").write_text("---")
    assert runner.invoke(app, ["mv", str(source), str(destination)]).exit_code == 0
    assert not GCSPath(source).exists()
    assert GCSPath(destination).is_dir()
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
    GCSPath(source).write_text("---")
    assert GCSPath(source).exists()
    assert runner.invoke(app, ["mv", source, destination]).exit_code == 0
    assert not GCSPath(source).exists()
    assert GCSPath(destination).is_file()


# @pytest.mark.parametrize("adapter", TEST_ADAPTERS)
# def test_cli_rename_files_across_buckets(with_adapter, bucket: str, other_bucket: str):
#     # Rename a single file across buckets
#     GCSPath(f"gs://{bucket}/rename/file.txt").write_text("---")
#     GCSPath(f"gs://{bucket}/rename/file.txt").rename(
#         f"gs://{other_bucket}/rename/other.txt"
#     )
#     assert not GCSPath(f"gs://{bucket}/rename/file.txt").exists()
#     assert GCSPath(f"gs://{other_bucket}/rename/other.txt").is_file()


# @pytest.mark.parametrize("adapter", TEST_ADAPTERS)
# def test_cli_rename_folders_in_bucket(with_adapter, bucket: str):
#     # Rename a folder in the same bucket
#     GCSPath(f"gs://{bucket}/rename/folder/one.txt").write_text("---")
#     GCSPath(f"gs://{bucket}/rename/folder/two.txt").write_text("---")
#     path = GCSPath(f"gs://{bucket}/rename/folder/")
#     new_path = GCSPath(f"gs://{bucket}/rename/other/")
#     path.rename(new_path)
#     assert not path.exists()
#     assert new_path.exists()
#     assert GCSPath(f"gs://{bucket}/rename/other/one.txt").is_file()
#     assert GCSPath(f"gs://{bucket}/rename/other/two.txt").is_file()


# @pytest.mark.parametrize("adapter", TEST_ADAPTERS)
# def test_cli_rename_folders_across_buckets(
#     with_adapter, bucket: str, other_bucket: str
# ):
#     # Rename a folder across buckets
#     GCSPath(f"gs://{bucket}/rename/folder/one.txt").write_text("---")
#     GCSPath(f"gs://{bucket}/rename/folder/two.txt").write_text("---")
#     path = GCSPath(f"gs://{bucket}/rename/folder/")
#     new_path = GCSPath(f"gs://{other_bucket}/rename/other/")
#     path.rename(new_path)
#     assert not path.exists()
#     assert new_path.exists()
#     assert GCSPath(f"gs://{other_bucket}/rename/other/one.txt").is_file()
#     assert GCSPath(f"gs://{other_bucket}/rename/other/two.txt").is_file()
