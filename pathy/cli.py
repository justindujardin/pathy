import typer

from .base import FluidPath, Pathy

app = typer.Typer(help="Pathy command line interface.")


@app.command()
def cp(from_location: str, to_location: str) -> None:
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
def mv(from_location: str, to_location: str) -> None:
    """
    Move a blob or folder of blobs from one path to another.
    """
    from_path: FluidPath = Pathy.fluid(from_location)
    to_path: FluidPath = Pathy.fluid(to_location)

    if from_path.is_file():
        # Copy prefix from the source if the to_path has none.
        #
        # e.g. "cp ./file.txt gs://bucket-name/" writes "gs://bucket-name/file.txt"
        if isinstance(to_path, Pathy) and to_path.prefix == "":
            to_path = to_path / from_path
        to_path.parent.mkdir(parents=True, exist_ok=True)
        to_path.write_bytes(from_path.read_bytes())
        from_path.unlink()
        return

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


@app.command()
def rm(
    location: str,
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Recursively remove files and folders."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print removed files and folders."
    ),
) -> None:
    """
    Remove a blob or folder of blobs from a given location.
    """
    path: FluidPath = Pathy.fluid(location)
    if not path.exists():
        typer.echo(f"rm: {path}: No such file or directory")
        raise typer.Exit(1)

    if path.is_dir():
        if not recursive:
            typer.echo(f"rm: {path}: is a directory")
            raise typer.Exit(1)
        selector = path.rglob("*") if recursive else path.glob("*")
        to_unlink = [b for b in selector if b.is_file()]
        for blob in to_unlink:
            if verbose:
                typer.echo(str(blob))
            blob.unlink()
        if path.exists():
            if verbose:
                typer.echo(str(path))
            path.rmdir()
    elif path.is_file():
        if verbose:
            typer.echo(str(path))
        path.unlink()


@app.command()
def ls(location: str) -> None:
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
