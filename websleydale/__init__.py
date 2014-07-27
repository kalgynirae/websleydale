import asyncio
import collections
import collections.abc
import pathlib
import shutil
import sys

from . import log
from . import sources
from . import util

__version__ = "2.0-alpha1"

_defaults = {}


def build(dest, root_coro):
    dest = pathlib.Path(dest)
    if dest.exists():
        if _yesno("Output directory {} exists.\nRemove it and continue?", dest):
            shutil.rmtree(str(dest))
        else:
            sys.exit(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(copy(root_coro, dest))


@asyncio.coroutine
def copy(source_coro, dest):
    source = (yield from source_coro).path
    log.debug("copy {} -> {}", source, dest)
    util.mkdir_if_needed(dest.parent)
    try:
        shutil.copy(str(source), str(dest))
    except IsADirectoryError:
        shutil.copytree(str(source), str(dest), copy_function=shutil.copy)
    return sources.SourceFile(dest)


@asyncio.coroutine
def directory(tree):
    coros = []
    path = util.temporary_dir()
    for destination, source_coro in tree.items():
        dest = path / destination
        #assert asyncio.iscoroutine(source_coro), log.format(
        #        "{}: not a coroutine: {}", dest, source_coro)
        coros.append(copy(source_coro, dest))
    yield from _run(coros)
    return sources.SourceFile(path)


def menu(items):
    return '<!--\n-->'.join(
        '<li><a href="{}">{}</a></li>'.format(href, name)
        for name, href in items
    )


@asyncio.coroutine
def pandoc(source_coro, *, header=None, footer=None, css=None, menu=None,
           template=None, toc=False):
    if template is None:
        template = _defaults['template']
    if menu is None:
        menu = _defaults['menu']

    source = yield from source_coro
    in_path = source.path
    out_path = util.temporary_file('.html')

    if header:
        header = (yield from header).path
    if footer:
        footer = (yield from footer).path
    if css:
        css = (yield from css).path
    if template:
        template = (yield from template).path

    args = [
        'pandoc',
        str(in_path),
        '--output=%s' % out_path,
        '--to=html5',
        '--standalone',
        '--preserve-tabs',
        '--highlight-style=tango',
    ]
    if css: args.append('--css=%s' % css)
    if footer: args.append('--include-after-body=%s' % footer)
    if header: args.append('--include-before-body=%s' % header)
    if menu: args.append('--variable=menu:%s' % menu)
    if template: args.append('--template=%s' % template)
    if toc: args.append('--toc')
    if source.info: args.append('--variable=source-info:%s' % source.info)

    log.debug("pandoc {}", args)
    process = yield from asyncio.create_subprocess_exec(*args)
    return_code = yield from process.wait()

    return sources.SourceFile(out_path)


@asyncio.coroutine
def _run(coros):
    for future in asyncio.as_completed(coros):
        try:
            result = yield from future
        except Exception as e:
            log.warning("{}: {}", e.__class__.__name__, str(e))


def set_defaults(**defaults):
    _defaults.update(defaults)


def _yesno(question, *args, default=False):
    choices = " (Y/n) " if default else " (y/N) "
    while True:
        answer = input(">> " + log.format(question, *args) + choices)
        if "y" == answer.lower():
            return True
        elif "n" == answer.lower():
            return False
        elif "" == answer:
            return default
