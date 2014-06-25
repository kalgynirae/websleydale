import os
import pathlib
import tempfile

from . import log

def mkdir_if_needed(path):
    try:
        path.mkdir(parents=True)
        log.info("Created directory {}", path)
    except FileExistsError:
        pass

_tempdir = None
def _make_tempdir():
    global _tempdir
    if _tempdir is None:
        _tempdir = tempfile.TemporaryDirectory(prefix="websleydale-")
        log.info("Using temporary directory {}", _tempdir)

def temporary_file(suffix=''):
    _make_tempdir()
    f, path = tempfile.mkstemp(suffix=suffix, dir=_tempdir.name)
    os.close(f)
    return pathlib.Path(path)

_tempdirs = []
def temporary_dir(prefix=''):
    _make_tempdir()
    t = tempfile.TemporaryDirectory(prefix=prefix, dir=_tempdir.name)
    _tempdirs.append(t)
    return pathlib.Path(t.name)
