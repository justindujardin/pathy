from pathlib import _Accessor as _PathlibAccessor  # type:ignore
from pathlib import _PosixFlavour as _PathlibPosixFlavour  # type:ignore
from pathlib import _WindowsFlavour as _PathlibWindowsFlavour  # type:ignore


class _Accessor(_PathlibAccessor):  # type:ignore
    pass


class _PosixFlavour(_PathlibPosixFlavour):  # type:ignore
    pass


class _WindowsFlavour(_PathlibWindowsFlavour):  # type:ignore
    pass
