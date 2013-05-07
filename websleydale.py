#!/usr/bin/python3
"""Usage: websleydale [-c <file>] -o <dir>

Options:
  -c <file>, --config <file>     Configuration file [default: config.yaml]
  -o <dir>, --output <dir>       Output direcgtory [default: ./build]
  -h, --help                     Show this message
  --version                      Print the version

"""
__version__ = "1.0"

import glob
import os
from os.path import abspath, basename, dirname, join
import shutil
from subprocess import CalledProcessError, check_call, check_output
import sys
from tempfile import TemporaryDirectory
from time import strftime

from docopt import docopt
import yaml

from terminal import log, _action, _error, _name, _path
from util import chdir, chdir_temp, listify, pandoc_version

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
except FileExistsError:
    log(_error("Output dir"), _path(OUTPUT_DIR),
        _error("exists, and we're not yet confident enough to clear it :/"))
    sys.exit(1)

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

        # Build list of sources
        sources = []
        for source in listify(info.get('source', [])):
            if source.startswith('http'):
                # Download the file and append the downloaded path
                check_call(['curl', '-O', source])
                sources.append(basename(source))
            else:
                sources.append(join(SOURCE_DIR, source))
        args.extend(sources)
        log(_action("Compiling"), _name(output_path))

        # Construct the menu?
        menu_items = []
        for item_name, item_url in config['menu']:
            active = ' class="active"' if item_url == name else ''
            i = '<li><a href="{item_url}"{active}>{item_name}</a></li>'
            menu_items.append(i.format(**locals()))
        args.extend(['-V', 'menu={}'.format('<!--\n-->'.join(menu_items))])

        # Create subdirs if needed
        subdirs = dirname(name)
        if subdirs:
            os.makedirs(join(OUTPUT_DIR, subdirs), exist_ok=True)
        try:
            check_call(args)
        except CalledProcessError:
            log(_error("Failed:"), _name(output_path))

# Copy static files
for source, dest in config.get('copy', {}).items():
    source_path = join(SOURCE_DIR, source)
    dest_path = join(OUTPUT_DIR, dest)
    log(_action("Copying"), _path(source_path), "->", _path(dest_path))
    try:
        shutil.rmtree(dest_path)
    except OSError:
        # Handle the dir-doesn't-exist error
        raise
    shutil.copytree(source_path, dest_path)
