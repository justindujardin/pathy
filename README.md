# Pathy: a python Path interface for bucket storage

[![Build status](https://travis-ci.org/justindujardin/pathy.svg?branch=master)](https://travis-ci.org/justindujardin/pathy)
[![Pypi version](https://badgen.net/pypi/v/pathy)](https://pypi.org/project/pathy/)

Pathy is a python package (_with type annotations_) for working with Bucket storage providers. It provides a CLI app for basic file operations between local files and remote buckets. It enables a smooth developer experience by supporting local file-system backed buckets during development and testing. It makes converting bucket blobs into local files a snap with optional local file caching of blobs.

## 🚀 Quickstart

You can install `pathy` from pip:

```bash
pip install pathy
```

The package exports the `Pathy` class and utilities for configuring the bucket storage provider to use. By default Pathy prefers GoogleCloudStorage paths of the form `gs://bucket_name/folder/blob_name.txt`. Internally Pathy can convert GCS paths to local files, allowing for a nice developer experience.

```python
from pathy import Pathy

# Any bucket you have access to will work
greeting = Pathy(f"gs://my_bucket/greeting.txt")
# The blob doesn't exist yet
assert not greeting.exists()
# Create it by writing some text
greeting.write_text("Hello World!")
# Now it exists
assert greeting.exists()
# Delete it
greeting.unlink()
# Now it doesn't
assert not greeting.exists()
```

## 🎛 API

<!-- NOTE: The below code is auto-generated. Update source files to change API documentation. -->
<!-- AUTO_DOCZ_START -->

# Pathy

```python
Pathy(self, args, kwargs)
```

Subclass of pathlib.Path that works with bucket storage providers.

## exists

```python
Pathy.exists(self: ~PathType) -> bool
```

Whether the path points to an existing Bucket, key or key prefix.

## fluid

```python
Pathy.fluid(
    path_candidate: Union[str, Pathy, pathlib.Path],
) -> Union[Pathy, pathlib.Path]
```

Helper to infer a pathlib.Path or Pathy from an input path or string.

The returned type is a union of the potential `FluidPath` types and will
type-check correctly against the minimum overlapping APIs of all the input
types.

If you need to use specific implementation details of a type, you
will need to narrow the return of this function to the desired type, e.g.

```python
# Narrow the type to a specific class
assert isinstance(path, Pathy), "must be Pathy"
# Use a member specific to that class
print(path.prefix)
```

## from_bucket

```python
Pathy.from_bucket(bucket_name: str) -> 'Pathy'
```

Helper to convert a bucket name into a Pathy without needing
to add the leading and trailing slashes

## glob

```python
Pathy.glob(self: ~PathType, pattern) -> Generator[~PathType, NoneType, NoneType]
```

Glob the given relative pattern in the Bucket / key prefix represented
by this path, yielding all matching files (of any kind)

## is_dir

```python
Pathy.is_dir(self: ~PathType) -> bool
```

Returns True if the path points to a Bucket or a key prefix, False if it
points to a full key path. False is returned if the path doesn’t exist.
Other errors (such as permission errors) are propagated.

## is_file

```python
Pathy.is_file(self: ~PathType) -> bool
```

Returns True if the path points to a Bucket key, False if it points to
Bucket or a key prefix. False is returned if the path doesn’t exist.
Other errors (such as permission errors) are propagated.

## iterdir

```python
Pathy.iterdir(self: ~PathType) -> Generator[~PathType, NoneType, NoneType]
```

When the path points to a Bucket or a key prefix, yield path objects of
the directory contents

## mkdir

```python
Pathy.mkdir(
    self: ~PathType,
    mode: int = 511,
    parents: bool = False,
    exist_ok: bool = False,
) -> None
```

Create a path bucket.
Bucket storage doesn't support folders explicitly, so mkdir will only create a bucket.

If exist_ok is false (the default), FileExistsError is raised if the
target Bucket already exists.

If exist_ok is true, OSError exceptions will be ignored.

if parents is false (the default), mkdir will create the bucket only
if this is a Bucket path.

if parents is true, mkdir will create the bucket even if the path
have a Key path.

mode argument is ignored.

## open

```python
Pathy.open(
    self: ~PathType,
    mode = 'r',
    buffering = 8192,
    encoding = None,
    errors = None,
    newline = None,
)
```

Opens the Bucket key pointed to by the path, returns a Key file object
that you can read/write with.

## owner

```python
Pathy.owner(self: ~PathType) -> Optional[str]
```

Returns the name of the user owning the Bucket or key.
Similarly to boto3's ObjectSummary owner attribute

## rename

```python
Pathy.rename(self: ~PathType, target: Union[str, ~PathType]) -> None
```

Rename this file or Bucket / key prefix / key to the given target.
If target exists and is a file, it will be replaced silently if the user
has permission. If path is a key prefix, it will replace all the keys with
the same prefix to the new target prefix. Target can be either a string or
another Pathy object.

## replace

```python
Pathy.replace(self: ~PathType, target: Union[str, ~PathType]) -> None
```

Renames this Bucket / key prefix / key to the given target.
If target points to an existing Bucket / key prefix / key, it will be
unconditionally replaced.

## resolve

```python
Pathy.resolve(self: ~PathType) -> ~PathType
```

Resolve the given path to remove any relative path specifiers.

## rglob

```python
Pathy.rglob(self: ~PathType, pattern) -> Generator[~PathType, NoneType, NoneType]
```

This is like calling Pathy.glob with "\*\*/" added in front of the given
relative pattern.

## rmdir

```python
Pathy.rmdir(self: ~PathType) -> None
```

Removes this Bucket / key prefix. The Bucket / key prefix must be empty

## samefile

```python
Pathy.samefile(self: ~PathType, other_path: ~PathType) -> bool
```

Returns whether this path points to the same Bucket key as other_path,
Which can be either a Path object, or a string

## stat

```python
Pathy.stat(self: ~PathType) -> pathy.client.BucketStat
```

Returns information about this path.
The result is looked up at each call to this method

## to_local

```python
Pathy.to_local(
    blob_path: Union[Pathy, str],
    recurse: bool = True,
) -> pathlib.Path
```

Get a bucket blob and return a local file cached version of it. The cache
is sensitive to the file updated time, and downloads new blobs as they become
available.

## touch

```python
Pathy.touch(self: ~PathType, mode: int = 438, exist_ok: bool = True)
```

Creates a key at this given path.

If the key already exists, the function succeeds if exist_ok is true
(and its modification time is updated to the current time), otherwise
FileExistsError is raised.

# use_fs

```python
use_fs(
    root: Optional[str, pathlib.Path, bool] = None,
) -> Optional[pathy.file.BucketClientFS]
```

Use a path in the local file-system to store blobs and buckets.

This is useful for development and testing situations, and for embedded
applications.

# get_fs_client

```python
get_fs_client() -> Optional[pathy.file.BucketClientFS]
```

Get the file-system client (or None)

# use_fs_cache

```python
use_fs_cache(
    root: Optional[str, pathlib.Path, bool] = None,
) -> Optional[pathlib.Path]
```

Use a path in the local file-system to cache blobs and buckets.

This is useful for when you want to avoid fetching large blobs multiple
times, or need to pass a local file path to a third-party library.

# get_fs_cache

```python
get_fs_cache() -> Optional[pathlib.Path]
```

Get the file-system client (or None)

# CLI

Pathy command line interface.

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `cp`: Copy a blob or folder of blobs from one...
- `ls`: List the blobs that exist at a given...
- `mv`: Move a blob or folder of blobs from one path...
- `rm`: Remove a blob or folder of blobs from a given...

## `cp`

Copy a blob or folder of blobs from one bucket to another.

**Usage**:

```console
$ cp [OPTIONS] FROM_LOCATION TO_LOCATION
```

**Options**:

- `--help`: Show this message and exit.

## `ls`

List the blobs that exist at a given location.

**Usage**:

```console
$ ls [OPTIONS] LOCATION
```

**Options**:

- `--help`: Show this message and exit.

## `mv`

Move a blob or folder of blobs from one path to another.

**Usage**:

```console
$ mv [OPTIONS] FROM_LOCATION TO_LOCATION
```

**Options**:

- `--help`: Show this message and exit.

## `rm`

Remove a blob or folder of blobs from a given location.

**Usage**:

```console
$ rm [OPTIONS] LOCATION
```

**Options**:

- `-r, --recursive`: Recursively remove files and folders.
- `-v, --verbose`: Print removed files and folders.
- `--help`: Show this message and exit.

<!-- AUTO_DOCZ_END -->
