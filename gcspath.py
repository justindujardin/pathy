"""gcspath provides a Pythonic API to GCS by wrapping google.cloud.storage with
a pathlib interface."""
from typing import Optional, Iterable, Union
from contextlib import suppress
from collections import namedtuple
from tempfile import NamedTemporaryFile
from functools import wraps, partial, lru_cache
from pathlib import _PosixFlavour, _Accessor, PurePath, Path
from io import RawIOBase, DEFAULT_BUFFER_SIZE, UnsupportedOperation
import gs_chunked_io

try:
    from google.cloud import storage
    from google.api_core import exceptions as gcs_errors
except ImportError:
    storage = None

__version__ = "0.0.1"
__all__ = (
    "register_configuration_parameter",
    "GCSPath",
    "PureGCSPath",
    "StatResult",
    "GCSDirEntry",
    "GCSWritable",
    "GCSReadable",
)

_SUPPORTED_OPEN_MODES = {"r", "br", "rb", "tr", "rt", "w", "wb", "bw", "wt", "tw"}


class _GCSFlavour(_PosixFlavour):
    is_supported = bool(storage)

    def parse_parts(self, parts):
        drv, root, parsed = super().parse_parts(parts)
        for part in parsed[1:]:
            if part == "..":
                index = parsed.index(part)
                parsed.pop(index - 1)
                parsed.remove(part)
        return drv, root, parsed

    def make_uri(self, path):
        uri = super().make_uri(path)
        return uri.replace("file:///", "gs://")


class _GCSConfigurationMap(dict):
    def __missing__(self, path):
        for parent in path.parents:
            if parent in self:
                return self[parent]
        return self.setdefault(Path("/"), {})


class _GCSAccessor(_Accessor):
    """
    An accessor implements a particular (system-specific or not)
    way of accessing paths on the filesystem.

    In this case this will access GCS service
    """

    gcs: storage.Client

    def __init__(self, **kwargs):
        if storage is not None:
            self.gcs = storage.Client()
        self.configuration_map = _GCSConfigurationMap()

    def get_blob(self, path: "GCSPath") -> Optional[storage.Blob]:
        """Get the blob associated with a path or return None"""
        bucket_name = self._bucket_name(path.bucket)
        if not bucket_name:
            return None
        try:
            bucket = self.gcs.lookup_bucket(bucket_name)
        except gcs_errors.ClientError:
            return None
        if bucket is None:
            return None
        key_name = str(path.key)
        return bucket.get_blob(key_name)

    def stat(self, path: "GCSPath"):
        bucket = self.gcs.get_bucket(self._bucket_name(path.bucket))
        blob: storage.Blob = bucket.get_blob(str(path.key))
        if blob is None:
            raise FileNotFoundError(path)
        return StatResult(size=blob.size, last_modified=blob.updated)

    def is_dir(self, path: "GCSPath"):
        if str(path) == path.root:
            return True
        bucket = self.gcs.get_bucket(self._bucket_name(path.bucket))
        return any(bucket.list_blobs(prefix=self._generate_prefix(path)))

    def exists(self, path: "GCSPath") -> bool:
        bucket_name = self._bucket_name(path.bucket)
        if not bucket_name:
            return any(self.gcs.list_buckets())
        try:
            bucket = self.gcs.lookup_bucket(bucket_name)
        except gcs_errors.ClientError:
            return False
        if not path.key:
            return bucket is not None
        if bucket is None:
            return False
        key_name = str(path.key)
        blob = bucket.get_blob(key_name)
        if blob is not None:
            return blob.exists(client=self.gcs)
        # Because we want all the parents of a valid blob (e.g. "directory" in
        # "directory/foo.file") to return True, we enumerate the blobs with a prefix
        # and compare the object names to see if they match a substring of the path
        for obj in self.gcs.list_blobs(bucket_name, prefix=key_name):
            if obj.name == key_name:
                return True
            if obj.name.startswith(key_name + path._flavour.sep):
                return True
        return False

    def scandir(self, path: "GCSPath"):
        bucket_name = self._bucket_name(path.bucket)
        if not bucket_name:
            for bucket in self.gcs.list_buckets():
                yield GCSDirEntry(bucket.name, is_dir=True)
            return
        bucket = self.gcs.get_bucket(bucket_name)
        sep = path._flavour.sep

        continuation_token = None
        while True:
            if continuation_token:
                response = bucket.list_blobs(
                    prefix=self._generate_prefix(path),
                    delimiter=sep,
                    page_token=continuation_token,
                )
            else:
                response = bucket.list_blobs(
                    prefix=self._generate_prefix(path), delimiter=sep
                )
            for page in response.pages:
                for folder in list(page.prefixes):
                    full_name = folder[:-1] if folder.endswith(sep) else folder
                    name = full_name.split(sep)[-1]
                    yield GCSDirEntry(name, is_dir=True)
                for item in page:
                    yield GCSDirEntry(
                        name=item.name.split(sep)[-1],
                        is_dir=False,
                        size=item.size,
                        last_modified=item.updated,
                    )
            if response.next_page_token is None:
                break
            continuation_token = response.next_page_token

    def listdir(self, path: "GCSPath"):
        return [entry.name for entry in self.scandir(path)]

    def open(
        self,
        path: "GCSPath",
        *,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None
    ):
        object_blob = self.get_blob(path)
        if object_blob is None and "w" not in mode:
            raise FileNotFoundError(str(path))
        if "r" in mode:
            return GCSReadable(
                object_blob,
                path=path,
                mode=mode,
                buffering=buffering,
                encoding=encoding,
                errors=errors,
                newline=newline,
            )
        return GCSWritable(
            self.gcs.lookup_bucket(self._bucket_name(path.bucket)),
            path=path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self, path: "GCSPath") -> Optional[str]:
        blob: Optional[storage.Blob] = self.get_blob(path)
        return blob.owner if blob is not None else None

    def rename(self, path: "GCSPath", target: "GCSPath"):
        source_bucket_name = self._bucket_name(path.bucket)
        source_bucket_key = str(path.key)
        bucket = self.gcs.lookup_bucket(source_bucket_name)

        # Single file
        if not self.is_dir(path):
            from_blob: storage.Blob = bucket.get_blob(str(path.key))
            target_bucket_name = self._bucket_name(target.bucket)
            target_bucket: storage.Bucket = self.gcs.get_bucket(target_bucket_name)
            target_bucket.copy_blob(from_blob, target_bucket, str(target.key))
            from_blob.bucket.delete_blob(from_blob.name)
            return

        # Folder with objects
        sep = path._flavour.sep
        continuation_token = None
        while True:
            prefix = self._generate_prefix(path)
            if continuation_token:
                response = from_blob.bucket.list_blobs(
                    prefix=prefix, delimiter=sep, page_token=continuation_token,
                )
            else:
                response = bucket.list_blobs(prefix=prefix, delimiter=sep)
            for page in response.pages:
                for item in page:
                    target_bucket_name = self._bucket_name(target.bucket)
                    target_key_name = item.name.replace(
                        source_bucket_key, str(target.key)
                    )
                    target_bucket = self.gcs.get_bucket(target_bucket_name)
                    target_bucket.copy_blob(item, target_bucket, target_key_name)
                    item.bucket.delete_blob(item.name)
            if response.next_page_token is None:
                break
            continuation_token = response.next_page_token

    def replace(self, path: "GCSPath", target: "GCSPath"):
        return self.rename(path, target)

    def rmdir(self, path: "GCSPath") -> None:
        bucket_name = self._bucket_name(path.bucket)
        key_name = str(path.key)
        bucket = self.gcs.get_bucket(bucket_name)
        bucket.delete_blobs(bucket.list_blobs(prefix=key_name))

    def mkdir(self, path: "GCSPath", mode) -> None:
        bucket_name = self._bucket_name(path.bucket)
        self.gcs.create_bucket(bucket_name)

    def _bucket_name(self, path: "GCSPath") -> str:
        if path is None:
            return
        return str(path.bucket)[1:]

    def _generate_prefix(self, path: "GCSPath") -> str:
        sep = path._flavour.sep
        if not path.key:
            return ""
        key_name = str(path.key)
        if not key_name.endswith(sep):
            return key_name + sep
        return key_name


def _string_parser(text, *, mode, encoding):
    if isinstance(text, memoryview):
        if "b" in mode:
            return text
        return text.obj.decode(encoding or "utf-8")
    if isinstance(text, (bytes, bytearray)):
        if "b" in mode:
            return text
        return text.decode(encoding or "utf-8")
    if isinstance(text, str):
        if "t" in mode or "r" == mode:
            return text
        return text.encode(encoding or "utf-8")
    raise RuntimeError()


class _PathNotSupportedMixin:
    _NOT_SUPPORTED_MESSAGE = "{method} is unsupported on GCS service"

    @classmethod
    def cwd(cls):
        """
        cwd class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.cwd.__qualname__)
        raise NotImplementedError(message)

    @classmethod
    def home(cls):
        """
        home class method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = cls._NOT_SUPPORTED_MESSAGE.format(method=cls.home.__qualname__)
        raise NotImplementedError(message)

    def chmod(self, mode):
        """
        chmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.chmod.__qualname__)
        raise NotImplementedError(message)

    def expanduser(self):
        """
        expanduser method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.expanduser.__qualname__
        )
        raise NotImplementedError(message)

    def lchmod(self, mode):
        """
        lchmod method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lchmod.__qualname__)
        raise NotImplementedError(message)

    def group(self):
        """
        group method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.group.__qualname__)
        raise NotImplementedError(message)

    def is_block_device(self):
        """
        is_block_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_block_device.__qualname__
        )
        raise NotImplementedError(message)

    def is_char_device(self):
        """
        is_char_device method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.is_char_device.__qualname__
        )
        raise NotImplementedError(message)

    def lstat(self):
        """
        lstat method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.lstat.__qualname__)
        raise NotImplementedError(message)

    def resolve(self):
        """
        resolve method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.resolve.__qualname__)
        raise NotImplementedError(message)

    def symlink_to(self, *args, **kwargs):
        """
        symlink_to method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(
            method=self.symlink_to.__qualname__
        )
        raise NotImplementedError(message)

    def unlink(self):
        """
        unlink method is unsupported on GCS service
        GCS don't have this file system action concept
        """
        message = self._NOT_SUPPORTED_MESSAGE.format(method=self.unlink.__qualname__)
        raise NotImplementedError(message)


_gcs_flavour = _GCSFlavour()
_gcs_accessor = _GCSAccessor()


def register_configuration_parameter(path, *, parameters):
    if not isinstance(path, PureGCSPath):
        raise TypeError(
            "path argument have to be a {} type. got {}".format(PureGCSPath, type(path))
        )
    if not isinstance(parameters, dict):
        raise TypeError(
            "parameters argument have to be a dict type. got {}".format(type(path))
        )
    _gcs_accessor.configuration_map[path].update(**parameters)


class PureGCSPath(PurePath):
    """
    PurePath subclass for GCS service.

    GCS is not a file-system but we can look at it like a POSIX system.
    """

    _flavour = _gcs_flavour
    __slots__ = ()

    @classmethod
    def from_uri(cls, uri):
        """
        from_uri class method create a class instance from url

        >> from gcspath import PureGCSPath
        >> PureGCSPath.from_url('gs://<bucket>/')
        << PureGCSPath('/<bucket>')
        """
        if not uri.startswith("gs://"):
            raise ValueError("...")
        return cls(uri[4:])

    @property
    def bucket(self):
        """
        bucket property
        return a new instance of only the bucket path
        """
        self._absolute_path_validation()
        if not self.is_absolute():
            raise ValueError("relative path don't have bucket")
        try:
            _, bucket, *_ = self.parts
        except ValueError:
            return None
        return type(self)(self._flavour.sep, bucket)

    @property
    def key(self):
        """
        bucket property
        return a new instance of only the key path
        """
        self._absolute_path_validation()
        key = self._flavour.sep.join(self.parts[2:])
        if not key:
            return None
        return type(self)(key)

    def as_uri(self):
        """
        Return the path as a 'gs' URI.
        """
        return super().as_uri()

    def _absolute_path_validation(self):
        if not self.is_absolute():
            raise ValueError("relative path has no bucket/key specification")


class GCSPath(_PathNotSupportedMixin, Path, PureGCSPath):
    """Path subclass for GCS service.

    Write files to and read files from the GCS service using pathlib.Path
    methods."""

    __slots__ = ()

    def stat(self):
        """
        Returns information about this path.
        The result is looked up at each call to this method
        """
        self._absolute_path_validation()
        if not self.key:
            return None
        return super().stat()

    def exists(self):
        """
        Whether the path points to an existing Bucket, key or key prefix.
        """
        self._absolute_path_validation()
        if not self.bucket:
            return True
        return self._accessor.exists(self)

    def is_dir(self):
        """
        Returns True if the path points to a Bucket or a key prefix, False if it 
        points to a full key path. False is returned if the path doesn’t exist.
        Other errors (such as permission errors) are propagated.
        """
        self._absolute_path_validation()
        if self.bucket and not self.key:
            return True
        return self._accessor.is_dir(self)

    def is_file(self):
        """
        Returns True if the path points to a Bucket key, False if it points to
        Bucket or a key prefix. False is returned if the path doesn’t exist.
        Other errors (such as permission errors) are propagated.
        """
        self._absolute_path_validation()
        if not self.bucket or not self.key:
            return False
        try:
            return bool(self.stat())
        except (gcs_errors.ClientError, FileNotFoundError):
            return False

    def iterdir(self):
        """
        When the path points to a Bucket or a key prefix, yield path objects of
        the directory contents
        """
        self._absolute_path_validation()
        yield from super().iterdir()

    def glob(self, pattern):
        """
        Glob the given relative pattern in the Bucket / key prefix represented by this path,
        yielding all matching files (of any kind)
        """
        yield from super().glob(pattern)

    def rglob(self, pattern):
        """
        This is like calling GCSPath.glob with "**/" added in front of the given relative pattern
        """
        yield from super().rglob(pattern)

    def open(
        self,
        mode="r",
        buffering=DEFAULT_BUFFER_SIZE,
        encoding=None,
        errors=None,
        newline=None,
    ):
        """
        Opens the Bucket key pointed to by the path, returns a Key file object that you can read/write with
        """
        self._absolute_path_validation()
        if mode not in _SUPPORTED_OPEN_MODES:
            raise ValueError(
                "supported modes are {} got {}".format(_SUPPORTED_OPEN_MODES, mode)
            )
        if buffering == 0 or buffering == 1:
            raise ValueError(
                "supported buffering values are only block sizes, no 0 or 1"
            )
        if "b" in mode and encoding:
            raise ValueError("binary mode doesn't take an encoding argument")

        if self._closed:
            self._raise_closed()
        return self._accessor.open(
            self,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def owner(self):
        """
        Returns the name of the user owning the Bucket or key.
        Similarly to boto3's ObjectSummary owner attribute
        """
        self._absolute_path_validation()
        if not self.is_file():
            raise FileNotFoundError(str(self))
        return self._accessor.owner(self)

    def rename(self, target):
        """
        Renames this file or Bucket / key prefix / key to the given target.
        If target exists and is a file, it will be replaced silently if the user
        has permission. If path is a key prefix, it will replace all the keys with
        the same prefix to the new target prefix. Target can be either a string or
        another GCSPath object.
        """
        self._absolute_path_validation()
        if not isinstance(target, type(self)):
            target = type(self)(target)
        target._absolute_path_validation()
        return super().rename(target)

    def replace(self, target):
        """
        Renames this Bucket / key prefix / key to the given target.
        If target points to an existing Bucket / key prefix / key, it will be
        unconditionally replaced.
        """
        return self.rename(target)

    def rmdir(self):
        """
        Removes this Bucket / key prefix. The Bucket / key prefix must be empty
        """
        self._absolute_path_validation()
        if self.is_file():
            raise NotADirectoryError()
        if not self.is_dir():
            raise FileNotFoundError()
        return super().rmdir()

    def samefile(self, other_path):
        """
        Returns whether this path points to the same Bucket key as other_path,
        Which can be either a Path object, or a string
        """
        self._absolute_path_validation()
        if not isinstance(other_path, Path):
            other_path = type(self)(other_path)
        return (
            self.bucket == other_path.bucket and self.key == self.key and self.is_file()
        )

    def touch(self, mode=0o666, exist_ok=True):
        """
        Creates a key at this given path.

        If the key already exists, the function succeeds if exist_ok is true
        (and its modification time is updated to the current time), otherwise
        FileExistsError is raised.
        """
        if self.exists() and not exist_ok:
            raise FileExistsError()
        self.write_text("")

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a path bucket.
        GCS Service doesn't support folders, therefore the mkdir method will
        only create the current bucket. If the bucket path already exists,
        FileExistsError is raised.

        If exist_ok is false (the default), FileExistsError is raised if the
        target Bucket already exists.

        If exist_ok is true, OSError exceptions will be ignored.

        if parents is false (the default), mkdir will create the bucket only
        if this is a Bucket path.

        if parents is true, mkdir will create the bucket even if the path
        have a Key path.

        mode argument is ignored.
        """
        try:
            if self.bucket is None:
                raise FileNotFoundError("No bucket in {} {}".format(type(self), self))
            if self.key is not None and not parents:
                raise FileNotFoundError(
                    "Only bucket path can be created, got {}".format(self)
                )
            if self.bucket.exists():
                raise FileExistsError("Bucket {} already exists".format(self.bucket))
            return super().mkdir(mode, parents=parents, exist_ok=exist_ok)
        except OSError:
            if not exist_ok:
                raise

    def is_mount(self):
        return False

    def is_symlink(self):
        return False

    def is_socket(self):
        return False

    def is_fifo(self):
        return False

    def _init(self, template=None):
        super()._init(template)
        if template is None:
            self._accessor = _gcs_accessor


class GCSWritable(RawIOBase):
    def __init__(
        self,
        bucket: storage.Bucket,
        *,
        path,
        mode="w",
        buffering=DEFAULT_BUFFER_SIZE,
        encoding=None,
        errors=None,
        newline=None
    ):
        super().__init__()
        self.bucket: storage.Bucket = bucket
        self.path: GCSPath = path
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self._cache = NamedTemporaryFile(
            mode=self.mode + "+" if "b" in self.mode else "b" + self.mode + "+",
            buffering=self.buffering,
            encoding=self.encoding,
            newline=self.newline,
        )
        self._string_parser = partial(
            _string_parser, mode=self.mode, encoding=self.encoding
        )

    def __getattr__(self, item):
        try:
            return getattr(self._cache, item)
        except AttributeError:
            return super().__getattribute__(item)

    def writable_check(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.writable():
                raise UnsupportedOperation("not writable")
            return method(self, *args, **kwargs)

        return wrapper

    def writable(self, *args, **kwargs):
        return "w" in self.mode

    @writable_check
    def write(self, text: Union[bytes, bytearray]):
        self._cache.write(self._string_parser(text))
        self._cache.seek(0)
        with gs_chunked_io.Writer(str(self.path.key), self.bucket) as writer:
            writer.write(self._cache.read())

    def writelines(self, lines: Iterable[Union[bytes, bytearray]]):
        strings = [self._string_parser(line) for line in lines]
        self.write("\n".join(strings))

    def readable(self) -> bool:
        return False

    def read(self, *args, **kwargs):
        raise UnsupportedOperation("not readable")

    def readlines(self, *args, **kwargs):
        raise UnsupportedOperation("not readable")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class GCSReadable(RawIOBase):
    def __init__(
        self,
        blob: storage.Blob,
        *,
        path,
        mode="b",
        buffering=DEFAULT_BUFFER_SIZE,
        encoding=None,
        errors=None,
        newline=None
    ):
        super().__init__()
        self.blob = blob
        self.path = path
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self._streaming_body = None
        self._string_parser = partial(
            _string_parser, mode=self.mode, encoding=self.encoding
        )

    def __iter__(self):
        return self

    def __next__(self):
        return self.readline()

    def __getattr__(self, item):
        try:
            return getattr(self._streaming_body, item)
        except AttributeError:
            return super().__getattribute__(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def readable_check(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.readable():
                raise UnsupportedOperation("not readable")
            return method(self, *args, **kwargs)

        return wrapper

    def readable(self):
        if "r" not in self.mode:
            return False
        with suppress(gcs_errors.ClientError):
            if self._streaming_body is None:
                self._streaming_body = gs_chunked_io.Reader(self.blob)
            return True
        return False

    @readable_check
    def read(self, *args, **kwargs):
        return self._string_parser(self._streaming_body.read())

    @readable_check
    def readlines(self, *args, **kwargs):
        return [line for line in iter(self.readline, self._string_parser(""))]

    @readable_check
    def readline(self):
        with suppress(StopIteration, ValueError):
            line = self._streaming_body.readline()
            return self._string_parser(line)
        return self._string_parser(b"")

    def write(self, *args, **kwargs):
        raise UnsupportedOperation("not writable")

    def writelines(self, *args, **kwargs):
        raise UnsupportedOperation("not writable")

    def writable(self, *args, **kwargs):
        return False


StatResult = namedtuple("StatResult", "size, last_modified")


class GCSDirEntry:
    def __init__(self, name, is_dir, size=None, last_modified=None):
        self.name = name
        self._is_dir = is_dir
        self._stat = StatResult(size=size, last_modified=last_modified)

    def __repr__(self):
        return "{}(name={}, is_dir={}, stat={})".format(
            type(self).__name__, self.name, self._is_dir, self._stat
        )

    def inode(self, *args, **kwargs):
        return None

    def is_dir(self):
        return self._is_dir

    def is_file(self):
        return not self._is_dir

    def is_symlink(self, *args, **kwargs):
        return False

    def stat(self):
        return self._stat
