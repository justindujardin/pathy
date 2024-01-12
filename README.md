# Pathy

[![Build](https://github.com/justindujardin/pathy/actions/workflows/python-package.yml/badge.svg)](https://github.com/justindujardin/pathy/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/justindujardin/pathy/branch/master/graph/badge.svg)](https://codecov.io/gh/justindujardin/pathy)
[![Pypi version](https://badgen.net/pypi/v/pathy)](https://pypi.org/project/pathy/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Pathy is a practical Python package with type annotations tailored for managing Cloud Bucket storage through a Path-like interface. It has an intuitive API and supports your [favorite](#google-cloud-storage) [cloud](#azure) [providers](#amazon-s3), facilitating file transfers between local systems and remote buckets. Ideal for seasoned developers, Pathy enables smooth local file system work during development, transitioning effortlessly to live APIs for deployment. It also simplifies converting bucket blobs into local files, offering an option for local file caching, and has a familiar CLI interface.

## 💾 Installation

You can install `pathy` from pip:

| Features             |      Install Command       |
| :------------------- | :------------------------: |
| Google Cloud Storage |  `pip install pathy[gcs]`  |
| Amazon S3            |  `pip install pathy[s3]`   |
| Azure                | `pip install pathy[azure]` |

## 🚀 Quickstart

Here's a quick run-down of how to get started offline if you intend to use Google Cloud Storage buckets when you ship.

```python
from pathy import Pathy, use_fs

# Use the local file-system for quicker development
use_fs()

# Create a bucket
Pathy("gs://my_bucket").mkdir(exist_ok=True)

# An excellent blob
greeting = Pathy(f"gs://my_bucket/greeting.txt")

# But it doesn't exist yet
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

## 🔐 Setup Credentials

For most cloud operations, you'll need credentials. Here's how to configure your credentials based on the supported cloud providers.

### Google Cloud Storage

Google recommends using a JSON credentials file, which you can specify by path:

```python
from google.oauth2 import service_account
from pathy import set_client_params

credentials = service_account.Credentials.from_service_account_file("./my-creds.json")
set_client_params("gs", credentials=credentials)
```

### Amazon S3

S3 uses a JSON credentials file, which you can specify by path:

```python
from pathy import set_client_params

set_client_params("s3", key_id="YOUR_ACCESS_KEY_ID", key_secret="YOUR_ACCESS_SECRET")
```

### Azure

Azure blob storage can be passed a `connection_string`:

```python
from pathy import set_client_params

set_client_params("azure", connection_string="YOUR_CONNECTION_STRING")
```

or a `BlobServiceClient` instance:

```python
from azure.storage.blob import BlobServiceClient
from pathy import set_client_params

service: BlobServiceClient = BlobServiceClient.from_connection_string(
    "YOUR_CONNECTION_STRING"
)
set_client_params("azure", service=service)
```

## ♻️ Semantic Versioning

Before Pathy reaches v1.0 the project is not guaranteed to have a consistent API, which means that types and classes may move around or be removed. That said, we try to be predictable when it comes to breaking changes, so the project uses semantic versioning to help users avoid breakage.

Specifically, new releases increase the `patch` semver component for new features and fixes, and the `minor` component when there are breaking changes. If you don't know much about semver strings, they're usually formatted `{major}.{minor}.{patch}` so increasing the `patch` component means incrementing the last number.

Consider a few examples:

| From Version | To Version | Changes are Breaking |
| :----------: | :--------: | :------------------: |
|    0.2.0     |   0.2.1    |          No          |
|    0.3.2     |   0.3.6    |          No          |
|    0.3.1     |   0.3.17   |          No          |
|    0.2.2     |   0.3.0    |         Yes          |

If you are concerned about breaking changes, you can pin the version in your requirements so that it does not go beyond the current semver `minor` component, for example if the current version was `0.11.0`:

```
pathy>=0.11.0,<0.12.0
```

## 📖 API

<!-- NOTE: The below code is auto-generated. Update source files to change API documentation. -->
<!-- AUTO_DOCZ_START -->

# Pathy <kbd>class</kbd>

```python (doc)
Pathy(self, paths)
```

Subclass of `PathBase` that works with bucket APIs.

## exists <kbd>method</kbd>

```python (doc)
Pathy.exists(self: 'Pathy') -> bool
```

Returns True if the path points to an existing bucket, blob, or prefix.

## fluid <kbd>classmethod</kbd>

```python (doc)
Pathy.fluid(
    path_candidate: Union[str, Pathy, PathlibPathEx],
) -> Union[Pathy, PathlibPathEx]
```

Infer either a Pathy or pathlib.Path from an input path or string.

The returned type is a union of the potential `FluidPath` types and will
type-check correctly against the minimum overlapping APIs of all the input
types.

If you need to use specific implementation details of a type, "narrow" the
return of this function to the desired type, e.g.

```python
from pathlib import Path
from pathy import FluidPath, Pathy

fluid_path: FluidPath = Pathy.fluid("gs://my_bucket/foo.txt")
# Narrow the type to a specific class
assert isinstance(fluid_path, Pathy), "must be Pathy"
# Use a member specific to that class
assert fluid_path.prefix == "foo.txt/"

# Or use a file-system path
posix_path: FluidPath = Pathy.fluid("/tmp/foo.txt")
assert isinstance(posix_path, Path), "must be pathlib.Path"
```

## from_bucket <kbd>classmethod</kbd>

```python (doc)
Pathy.from_bucket(bucket_name: str, scheme: str = 'gs') -> 'Pathy'
```

Initialize a Pathy from a bucket name. This helper adds a trailing slash and
the appropriate prefix.

```python
from pathy import Pathy

assert str(Pathy.from_bucket("one")) == "gs://one/"
assert str(Pathy.from_bucket("two")) == "gs://two/"
```

## glob <kbd>method</kbd>

```python (doc)
Pathy.glob(
    self: 'Pathy',
    pattern: str,
    case_sensitive: Optional[bool] = None,
    follow_symlinks: Optional[bool] = None,
) -> Generator[Pathy, NoneType, NoneType]
```

Perform a glob match relative to this Pathy instance, yielding all matched
blobs.

## is_dir <kbd>method</kbd>

```python (doc)
Pathy.is_dir(self: 'Pathy', follow_symlinks: bool = True) -> bool
```

Determine if the path points to a bucket or a prefix of a given blob
in the bucket.

Returns True if the path points to a bucket or a blob prefix.
Returns False if it points to a blob or the path doesn't exist.

## is_file <kbd>method</kbd>

```python (doc)
Pathy.is_file(self: 'Pathy', follow_symlinks: bool = True) -> bool
```

Determine if the path points to a blob in the bucket.

Returns True if the path points to a blob.
Returns False if it points to a bucket or blob prefix, or if the path doesn’t
exist.

## ls <kbd>method</kbd>

```python (doc)
Pathy.ls(self: 'Pathy') -> Generator[BlobStat, NoneType, NoneType]
```

List blob names with stat information under the given path.

This is considerably faster than using iterdir if you also need
the stat information for the enumerated blobs.

Yields BlobStat objects for each found blob.

## mkdir <kbd>method</kbd>

```python (doc)
Pathy.mkdir(
    self,
    mode: int = 511,
    parents: bool = False,
    exist_ok: bool = False,
) -> None
```

Create a bucket from the given path. Since bucket APIs only have implicit
folder structures (determined by the existence of a blob with an overlapping
prefix) this does nothing other than create buckets.

If parents is False, the bucket will only be created if the path points to
exactly the bucket and nothing else. If parents is true the bucket will be
created even if the path points to a specific blob.

The mode param is ignored.

Raises FileExistsError if exist_ok is false and the bucket already exists.

## open <kbd>method</kbd>

```python (doc)
Pathy.open(
    self: 'Pathy',
    mode: str = 'r',
    buffering: int = 8192,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
) -> IO[Any]
```

Open the given blob for streaming. This delegates to the `smart_open`
library that handles large file streaming for a number of bucket API
providers.

## owner <kbd>method</kbd>

```python (doc)
Pathy.owner(self: 'Pathy') -> Optional[str]
```

Returns the name of the user that owns the bucket or blob
this path points to. Returns None if the owner is unknown or
not supported by the bucket API provider.

## rename <kbd>method</kbd>

```python (doc)
Pathy.rename(
    self: 'Pathy',
    target: Union[str, pathlib_abc.PurePathBase],
) -> 'Pathy'
```

Rename this path to the given target.

If the target exists and is a file, it will be replaced silently if the user
has permission.

If path is a blob prefix, it will replace all the blobs with the same prefix
to match the target prefix.

## replace <kbd>method</kbd>

```python (doc)
Pathy.replace(
    self: 'Pathy',
    target: Union[str, pathlib_abc.PurePathBase],
) -> 'Pathy'
```

Renames this path to the given target.

If target points to an existing path, it will be replaced.

## resolve <kbd>method</kbd>

```python (doc)
Pathy.resolve(self, strict: bool = False) -> 'Pathy'
```

Resolve the given path to remove any relative path specifiers.

```python
from pathy import Pathy

path = Pathy("gs://my_bucket/folder/../blob")
assert path.resolve() == Pathy("gs://my_bucket/blob")
```

## rmdir <kbd>method</kbd>

```python (doc)
Pathy.rmdir(self: 'Pathy') -> None
```

Removes this bucket or blob prefix. It must be empty.

## samefile <kbd>method</kbd>

```python (doc)
Pathy.samefile(
    self: 'Pathy',
    other_path: Union[str, bytes, int, pathlib_abc.PathBase],
) -> bool
```

Determine if this path points to the same location as other_path.

## stat <kbd>method</kbd>

```python (doc)
Pathy.stat(self: 'Pathy', follow_symlinks: bool = True) -> pathy.BlobStat
```

Returns information about this bucket path.

## to_local <kbd>classmethod</kbd>

```python (doc)
Pathy.to_local(
    blob_path: Union[Pathy, str],
    recurse: bool = True,
) -> pathlib.Path
```

Download and cache either a blob or a set of blobs matching a prefix.

The cache is sensitive to the file updated time, and downloads new blobs
as their updated timestamps change.

## touch <kbd>method</kbd>

```python (doc)
Pathy.touch(self: 'Pathy', mode: int = 438, exist_ok: bool = True) -> None
```

Create a blob at this path.

If the blob already exists, the function succeeds if exist_ok is true
(and its modification time is updated to the current time), otherwise
FileExistsError is raised.

## unlink <kbd>method</kbd>

```python (doc)
Pathy.unlink(self: 'Pathy') -> None
```

Delete a link to a blob in a bucket.

# BlobStat <kbd>dataclass</kbd>

```python (doc)
BlobStat(
    self,
    name: str,
    size: Optional[int],
    last_modified: Optional[int],
) -> None
```

Stat for a bucket item

# use_fs <kbd>function</kbd>

```python (doc)
use_fs(
    root: Optional[str, pathlib_abc.PathBase, pathy.PathlibPathEx, bool] = None,
) -> Optional[pathy.BucketClientFS]
```

Use a path in the local file-system to store blobs and buckets.

This is useful for development and testing situations, and for embedded
applications.

# get_fs_client <kbd>function</kbd>

```python (doc)
get_fs_client() -> Optional[pathy.BucketClientFS]
```

Get the file-system client (or None)

# use_fs_cache <kbd>function</kbd>

```python (doc)
use_fs_cache(
    root: Optional[str, pathlib_abc.PathBase, pathy.PathlibPathEx, bool] = None,
) -> Optional[pathy.PathlibPathEx]
```

Use a path in the local file-system to cache blobs and buckets.

This is useful for when you want to avoid fetching large blobs multiple
times, or need to pass a local file path to a third-party library.

# get_fs_cache <kbd>function</kbd>

```python (doc)
get_fs_cache() -> Optional[pathy.PathlibPathEx]
```

Get the folder that holds file-system cached blobs and timestamps.

# set_client_params <kbd>function</kbd>

```python (doc)
set_client_params(scheme: str, kwargs: Any) -> None
```

Specify args to pass when instantiating a service-specific Client
object. This allows for passing credentials in whatever way your underlying
client library prefers.

# CLI

Pathy command line interface. (v0.11.0)

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
- `mv`: Move a blob or folder of blobs from one...
- `rm`: Remove a blob or folder of blobs from a...

## `cp`

Copy a blob or folder of blobs from one bucket to another.

**Usage**:

```console
$ cp [OPTIONS] FROM_LOCATION TO_LOCATION
```

**Arguments**:

- `FROM_LOCATION`: [required]
- `TO_LOCATION`: [required]

**Options**:

- `--help`: Show this message and exit.

## `ls`

List the blobs that exist at a given location.

**Usage**:

```console
$ ls [OPTIONS] LOCATION
```

**Arguments**:

- `LOCATION`: [required]

**Options**:

- `-l, --long`: Print long style entries with updated time and size shown.
- `--help`: Show this message and exit.

## `mv`

Move a blob or folder of blobs from one path to another.

**Usage**:

```console
$ mv [OPTIONS] FROM_LOCATION TO_LOCATION
```

**Arguments**:

- `FROM_LOCATION`: [required]
- `TO_LOCATION`: [required]

**Options**:

- `--help`: Show this message and exit.

## `rm`

Remove a blob or folder of blobs from a given location.

**Usage**:

```console
$ rm [OPTIONS] LOCATION
```

**Arguments**:

- `LOCATION`: [required]

**Options**:

- `-r, --recursive`: Recursively remove files and folders.
- `-v, --verbose`: Print removed files and folders.
- `--help`: Show this message and exit.

<!-- AUTO_DOCZ_END -->

# Credits

Pathy is originally based on the [S3Path](https://github.com/liormizr/s3path) project, which provides a Path interface for S3 buckets.
