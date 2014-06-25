import asyncio
import collections
import collections.abc
import pathlib
import shutil

from . import log
from . import sources
from . import util

__version__ = "2.0-alpha1"

def _flatten(tree, prefix):
    for key, value in tree.items():
        path = prefix / key
        if isinstance(value, collections.abc.Mapping):
            yield from _flatten(value, prefix=path)
        else:
            yield (path, value)

def build(output_dir, tree):
    output_dir = pathlib.Path(output_dir)
    util.mkdir_if_needed(output_dir)
    log.info("Outputting to {}", output_dir)
    things = collections.OrderedDict(sorted(_flatten(tree, output_dir)))
    tasks = []
    for destination, source_coro in things.items():
        assert asyncio.iscoroutine(source_coro), (
                "%s: not a coroutine: %r" % (destination, source_coro))
        tasks.append(asyncio.Task(copy(source_coro, destination)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

def copy(source_coro, dest):
    source = yield from source_coro
    log.info("Renaming {} to {}", source, dest)
    util.mkdir_if_needed(dest.parent)
    source.rename(dest)
