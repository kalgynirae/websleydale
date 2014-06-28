import asyncio
import collections
import collections.abc
import pathlib

from . import actions
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

def _run(coros):
    for future in asyncio.as_completed(coros):
        try:
            result = yield from future
        except Exception as e:
            log.warning("{}: {}", e.__class__.__name__, str(e))

def build(output_dir, tree):
    output_dir = pathlib.Path(output_dir)
    util.mkdir_if_needed(output_dir)
    log.info("Outputting to {}", output_dir)

    coros = []
    for destination, source_coro in _flatten(tree, output_dir):
        assert asyncio.iscoroutine(source_coro), (
                "%s: not a coroutine: %r" % (destination, source_coro))
        coros.append(actions.move(source_coro, destination))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run(coros))
