#!/usr/bin/python3

"""Websleydale compiles your web site from a bunch of source files.

Usage: websleydale [-c <file>] -o <dir>

Options:
  -c <file>, --config <file>     Configuration file [default: config.yaml]
  -o <dir>, --output <dir>       Output direcgtory [default: ./build]
  -h, --help                     Show this message
  --version                      Print the version
"""

__version__ = "1.0"

import contextlib
import os
from os.path import abspath, basename, dirname, join
import shutil
from subprocess import CalledProcessError, check_call, check_output
import sys
from tempfile import TemporaryDirectory
from time import strftime

from docopt import docopt
import yaml

@contextlib.contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)

@contextlib.contextmanager
def chdir_temp():
    with TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            yield tempdir

def highlighter(color=None, bg_color=None, style=None):
    SET_FG_COLOR = '\x1b[3{}m'
    SET_BG_COLOR = '\x1b[4{}m'
    SET_STYLE = '\x1b[{}m'
    COLOR_NAMES = 'black red green yellow blue magenta cyan white'.split()
    COLORS = {color: index for index, color in enumerate(COLOR_NAMES)}
    STYLES = {'bold': 1, 'underline': 4}
    RESET = '\x1b[0m'
    q = ((SET_FG_COLOR.format(COLORS[color]) if color else '') +
         (SET_BG_COLOR.format(COLORS[bg_color]) if bg_color else '') +
         (SET_STYLE.format(STYLES[style]) if style else '') +
         '{}' + (RESET if style or color else ''))
    def highlight(s):
        return q.format(s)
    return highlight

def listify(item):
    return item if isinstance(item, list) else [item]

def log(*args, **kwargs):
    print('▶', end=' ')
    print(*args, **kwargs)

def pandoc_version():
    output = check_output(['pandoc', '-v']).decode()
    return output.split('\n')[0].split()[1]

def main():
    _action = highlighter('yellow')
    _error = highlighter('red')
    _name = highlighter('green')
    _path = highlighter('blue')

    # Parse arguments
    arguments = docopt(__doc__, version=__version__)

    # Load the configuration and print it for science
    log(_action("Loading"), _path(arguments['--config']))
    with open(arguments['--config']) as f:
        config = yaml.load(f)

    SOURCE_DIR = abspath(dirname(arguments['--config']))
    OUTPUT_DIR = abspath(arguments['--output'])

    # Create the output directory
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except FileExistsError as e:
        if e.errno == 17:
            pass
        else:
            raise

    # Grab compile-time data
    vars = {}
    vars['time'] = strftime('%Y-%m-%dT%H:%M:%S%z')
    try:
        with chdir(SOURCE_DIR):
            vars['version'] = (check_output(['git', 'describe', '--tags'])
                               .decode().strip())
    except CalledProcessError:
        pass
    vars['pandoc-version'] = pandoc_version()
    vars['websleydale-version'] = __version__

    # Compile pages
    with chdir_temp() as temp_dir:
        for name, info in config['pages'].items():
            output_path = join(OUTPUT_DIR, name)
            args = ['pandoc', '--to=html5', '--standalone',
                    '--highlight-style=tango',
                    '--template={}'.format(join(SOURCE_DIR, config['template'])),
                    '--output={}'.format(output_path)]
            if info.get('toc', False):
                args.append('--toc')
            for header in listify(info.get('header', [])):
                args.extend(['-H', join(SOURCE_DIR, header)])
            for var, value in vars.items():
                args.extend(['-V', '{}={}'.format(var, value)])

            # Construct the menu?
            menu_items = []
            for item_name, item_url in config['menu']:
                active = ' class="active"' if item_url == name else ''
                i = '<li><a href="{item_url}"{active}>{item_name}</a></li>'
                menu_items.append(i.format(**locals()))
            args.extend(['-V', 'menu={}'.format('<!--\n-->'.join(menu_items))])

            # Build list of sources
            for source in listify(info.get('source', [])):
                if source.startswith('http'):
                    # Download the file and append the downloaded path
                    log(_action("Fetching"), _path(source))
                    check_call(['curl', '-OsS', source])
                    args.append(basename(source))
                else:
                    args.append(join(SOURCE_DIR, source))

            # Create subdirs if needed
            subdirs = dirname(name)
            if subdirs:
                os.makedirs(join(OUTPUT_DIR, subdirs), exist_ok=True)
            log(_action("Building"), _name(name))
            try:
                check_call(args)
            except CalledProcessError:
                log(_error("Failed:"), _name(name))

    # Copy static files
    for source, dest in config.get('copy', {}).items():
        source_path = join(SOURCE_DIR, source)
        dest_path = join(OUTPUT_DIR, dest)
        log(_action("Copying"), _path(source_path), _action("->"),
            _path(dest_path))
        try:
            shutil.rmtree(dest_path)
        except FileNotFoundError:
            pass
        shutil.copytree(source_path, dest_path)
    return None

if __name__ == '__main__':
    sys.exit(main())
