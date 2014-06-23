import asyncio
import collections
import collections.abc
import pathlib
import shutil

from . import log
from . import sources

__version__ = "2.0-alpha1"

def _flatten(tree, prefix=pathlib.Path()):
    for key, value in tree.items():
        path = prefix / key
        if isinstance(value, collections.abc.Mapping):
            yield from _flatten(value, prefix=path)
        else:
            yield (path, value)

def build(tree):
    things = collections.OrderedDict(sorted(_flatten(tree)))
    tasks = []
    for destination, source_coro in things.items():
        assert asyncio.iscoroutine(source_coro), (
                "%s: not a coroutine: %r" % (destination, source_coro))
        tasks.append(asyncio.Task(copy(source_coro, destination)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

def copy(source_coro, dest):
    source = yield from source_coro
    log.info("Copying {} to {}", source, dest)
    #shutil.copy(source, dest)
