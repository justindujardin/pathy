#!/usr/bin/env python3.7
from pathlib import Path

import typer
from pathy import Pathy, FluidPath

app = typer.Typer()


@app.command()
def cp(from_location: str, to_location: str):
    """
    Copy a blob or folder of blobs from one bucket to another.
    """
    from_path: FluidPath = Pathy.fluid(from_location)
    if not from_path.exists():
        raise ValueError(f"from_path is not an existing Path or Pathy: {from_path}")
    to_path: FluidPath = Pathy.fluid(to_location)
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
        if isinstance(to_path, Pathy) and to_path.prefix == "":
            to_path = to_path / from_path

        to_path.parent.mkdir(parents=True, exist_ok=True)
        to_path.write_bytes(from_path.read_bytes())


@app.command()
def mv(from_location: str, to_location: str):
    """
    Move a blob or folder of blobs from one path to another.
    """
    from_path: FluidPath = Pathy.fluid(from_location)
    if not from_path.exists():
        raise ValueError(f"from_path is not an existing Path or Pathy: {from_path}")
    to_path: FluidPath = Pathy.fluid(to_location)
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
        if isinstance(to_path, Pathy) and to_path.prefix == "":
            to_path = to_path / from_path
        to_path.parent.mkdir(parents=True, exist_ok=True)
        to_path.write_bytes(from_path.read_bytes())
        from_path.unlink()


@app.command()
def rm(location: str, strict: bool = False):
    """
    Remove a blob or folder of blobs from a given location.
    """
    path: FluidPath = Pathy.fluid(location)
    if not path.exists() and strict:
        raise ValueError(f"from_path is not an existing Path or Pathy: {path}")
    if path.is_dir():
        to_unlink = [b for b in path.rglob("*") if b.is_file()]
        for blob in to_unlink:
            blob.unlink()
        if path.exists():
            path.rmdir()
    elif path.is_file():
        path.unlink()


@app.command()
def ls(location: str):
    """
    List the blobs that exist at a given location.
    """
    path: FluidPath = Pathy.fluid(location)
    if not path.exists() or path.is_file():
        typer.echo(f"ls: {path}: No such file or directory")
        return
    for file in path.iterdir():
        typer.echo(file)


if __name__ == "__main__":
    app()
