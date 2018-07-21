import asyncio
import collections
import collections.abc
import contextlib
import logging
import pathlib
import shutil
import subprocess
import sys
import traceback

from . import log
from . import sources
from . import util

__version__ = '2.0-alpha2'

_defaults = {}


def build(dest, root_coro):
    dest = pathlib.Path(dest)
    if dest.exists():
        if ask('Output directory {} exists.\nRemove it and continue?', dest):
            shutil.rmtree(str(dest))
        else:
            sys.exit(1)
    with contextlib.closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(copy(root_coro, dest))


async def copy(source_coro, dest):
    source = (await source_coro).path
    log.debug('copy {} -> {}', source, dest)
    util.mkdir_if_needed(dest.parent)
    try:
        shutil.copy(str(source), str(dest))
    except IsADirectoryError:
        shutil.copytree(str(source), str(dest), copy_function=shutil.copy)
    return sources.SourceFile(dest)


async def directory(tree, *, dirlist=None):
    coros = []
    path = util.temporary_dir()
    if dirlist is not None:
        tree = collections.ChainMap(tree, {
            ".header.html": pandoc(
                None,
                template=_defaults["header_template"],
                title=dirlist,
            ),
            ".footer.html": pandoc(
                None,
                template=_defaults["footer_template"],
            ),
        })
    for destination, source_coro in tree.items():
        dest = path / destination
        #assert asyncio.iscoroutine(source_coro), log.format(
        #        '{}: not a coroutine: {}', dest, source_coro)
        coros.append(copy(source_coro, dest))
    await _run(coros)
    return sources.SourceFile(path)


def menu(items):
    return '<!--\n-->'.join(
        '<li><a href="{}">{}</a></li>'.format(href, name)
        for name, href in items
    )


async def pandoc(source_coro, *, header=None, footer=None, css=None, menu=None,
           template=None, title=None, toc=False):
    if template is None:
        template = _defaults['template']
    if menu is None:
        menu = _defaults['menu']

    if source_coro is None:
        source = sources.SourceFile("/dev/null")
    else:
        source = await source_coro

    in_path = source.path
    out_path = util.temporary_file('.html')

    if header:
        header = (await header).path
    if footer:
        footer = (await footer).path
    if css:
        css = (await css).path
    if template:
        template = (await template).path

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
    if header: args.append('--include-in-header=%s' % header)
    if menu: args.append('--variable=menu:%s' % menu)
    if template: args.append('--template=%s' % template)
    if title: args.append('--variable=pagetitle:%s' % title)
    if toc: args.append('--toc')
    if source.info: args.append('--variable=source-info:%s' % source.info)

    log.debug('pandoc {}', args)
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if stderr:
        log.warning('pandoc stderr for input {}:\n{}', in_path, stderr.decode())

    return sources.SourceFile(out_path)


async def _run(coros):
    for future in asyncio.as_completed(coros):
        try:
            result = await future
        except Exception as e:
            log.warning('{}: {}', e.__class__.__name__, str(e))
            traceback.print_exc()


def set_defaults(**defaults):
    # We need to be able to await these values multiple times; futures let us do that
    futured = {
        key: asyncio.ensure_future(value) if asyncio.iscoroutine(value) else value
        for key, value in defaults.items()
    }
    _defaults.update(futured)


def ask(question, *args, default=False):
    choices = ' (Y/n) ' if default else ' (y/N) '
    while True:
        answer = input('>> ' + log.format(question, *args) + choices)
        if 'y' == answer.lower():
            return True
        elif 'n' == answer.lower():
            return False
        elif '' == answer:
            return default
