#!/usr/bin/env python3.7
from pathlib import Path

import typer
from gcspath import GCSPath, FluidPath

app = typer.Typer()


@app.command()
def cp(from_location: str, to_location: str):
    """
    Copy a blob or folder of blobs from one bucket to another.
    """
    from_path: FluidPath = GCSPath.fluid(from_location)
    if not from_path.exists():
        raise ValueError(f"from_path is not an existing Path or GCSPath: {from_path}")
    to_path: FluidPath = GCSPath.fluid(to_location)
    if from_path.is_dir():
        to_path.mkdir(parents=True, exist_ok=True)
        for blob in from_path.rglob("*"):
            if not blob.is_file():
                continue
            to_blob = to_path / str(blob.relative_to(from_path))
            to_blob.write_bytes(blob.read_bytes())
    elif from_path.is_file():
        # Copy prefix from the source if the to_path has none.
        #
        # e.g. "cp ./file.txt gs://bucket-name/" writes "gs://bucket-name/file.txt"
        if isinstance(to_path, GCSPath) and to_path.prefix == "":
            to_path = to_path / from_path

        to_path.parent.mkdir(parents=True, exist_ok=True)
        to_path.write_bytes(from_path.read_bytes())


@app.command()
def mv(from_location: str, to_location: str):
    """
    Move a blob or folder of blobs from one path to another.
    """
    from_path: FluidPath = GCSPath.fluid(from_location)
    if not from_path.exists():
        raise ValueError(f"from_path is not an existing Path or GCSPath: {from_path}")
    to_path: FluidPath = GCSPath.fluid(to_location)
    if from_path.is_dir():
        to_path.mkdir(parents=True, exist_ok=True)
        to_unlink = []
        for blob in from_path.rglob("*"):
            if not blob.is_file():
                continue
            to_blob = to_path / str(blob.relative_to(from_path))
            to_blob.write_bytes(blob.read_bytes())
            to_unlink.append(blob)
        for blob in to_unlink:
            blob.unlink()
        if from_path.is_dir():
            from_path.rmdir()
    elif from_path.is_file():
        # Copy prefix from the source if the to_path has none.
        #
        # e.g. "cp ./file.txt gs://bucket-name/" writes "gs://bucket-name/file.txt"
        if isinstance(to_path, GCSPath) and to_path.prefix == "":
            to_path = to_path / from_path
        to_path.parent.mkdir(parents=True, exist_ok=True)
        to_path.write_bytes(from_path.read_bytes())
        from_path.unlink()


if __name__ == "__main__":
    app()
