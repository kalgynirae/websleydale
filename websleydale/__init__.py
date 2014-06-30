import asyncio
import collections
import collections.abc
import pathlib

from . import actions
from . import log
from . import sources
from . import util

__version__ = "2.0-alpha1"

def build(output_path, tree):
    output_path = pathlib.Path(output_path)
    util.mkdir_if_needed(output_path)
    log.info("Outputting to {}", output_path.resolve())
    return

    coros = []
    for destination, source_coro in _flatten(tree, output_path):
        assert asyncio.iscoroutine(source_coro), (
                "%s: not a coroutine: %r" % (destination, source_coro))
        coros.append(actions.move(source_coro, destination))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run(coros))

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
