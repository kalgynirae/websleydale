import asyncio
import functools
import shutil

from . import log
from . import util

def index(tree):
    assert 'index.html' not in tree
    tree['index.html'] = pandoc(_index_page(tree))
    return tree

def _index_page(tree):
    yield from asyncio.sleep(0)
    out_path = util.temporary_file('.html')
    return out_path

def move(source_coro, dest):
    source = yield from source_coro
    log.info("{} -> {}", source, dest)
    util.mkdir_if_needed(dest.parent)
    shutil.move(str(source), str(dest))
    return dest

@asyncio.coroutine
def pandoc(in_path_coro, *, header=None, template=None, toc=False):
    in_path = yield from in_path_coro
    out_path = util.temporary_file('.html')

    args = ['pandoc', str(in_path), '--output=%s' % out_path, '--to=html5',
            '--standalone']
    if toc:
        args.append('--toc')
    log.info("pandoc {} --output={}", in_path, out_path)

    process = yield from asyncio.create_subprocess_exec(*args)
    return_code = yield from process.wait()

    return out_path
