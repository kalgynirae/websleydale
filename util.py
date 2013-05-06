import contextlib
import functools
import os
import os.path
from subprocess import check_output
from tempfile import TemporaryDirectory

@contextlib.contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    try: yield
    finally:
        os.chdir(cwd)

@contextlib.contextmanager
def chdir_temp():
    with TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            yield tempdir

def listify(item):
    return item if isinstance(item, list) else [item]

def pandoc_version():
    output = check_output(['pandoc', '-v']).decode()
    return output.split('\n')[0].split()[1]
