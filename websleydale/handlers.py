import asyncio
import functools

from . import log
from .util import temporary_file

def index(tree):
    assert 'index.html' not in tree
    tree['index.html'] = pandoc(_index_page(tree))
    return tree

def _index_page(tree):
    yield from asyncio.sleep(0)
    out_path = temporary_file('.html')
    return out_path

@asyncio.coroutine
def pandoc(in_path_coro, *, header=None, template=None, toc=False):
    in_path = yield from in_path_coro
    out_path = temporary_file('.html')

    args = ['pandoc', in_path, '--output=%s' % out_path, '--to=html5',
            '--standalone']
    if toc:
        args.append('--toc')
    log.info("Pandocing {} to {}", in_path, out_path)
    #TODO: process = yield from asyncio.create_subprocess_exec(*args)
    #return_code = yield from process.wait()

    return out_path
