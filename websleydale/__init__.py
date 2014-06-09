import collections.abc
import pathlib

from . import sources
from . import util

__version__ = "2.0-alpha1"

def build(things, *, dest_dir="build", menu=None, prefix=None, redirects=None,
          template=None):
    if prefix is None:
        prefix = pathlib.Path(dest_dir)
    if not prefix.exists():
        prefix.mkdir()
    util.mkdir_if_needed(dest_dir)
    for path_component, thing in things.items():
        path = prefix / path_component
        if isinstance(thing, collections.abc.Mapping):
            build(thing, dest_dir=dest_dir, menu=menu, prefix=path,
                  redirects=redirects, template=template)
        else:
            print("{}: {!r}".format(util._path(path), thing))

def pandoc(file, header=None, toc=False):
    return file

def index(things):
    if "index.html" in things:
        raise ValueError("index.html already exists")
    things["index.html"] = pandoc(index_page_generator(things))
    return things

def index_page_generator(things):
    yield "INDEX PAGE!!"
