#!/usr/bin/python3
"""Usage: websleydale [--config <file>]

Options:
  -c <file>, --config <file>     Configuration file [default: config.yaml]
  -h, --help                     Show this message
  --version                      Print the version

"""
__version__ = 1

import glob
import os
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

# Create the output directory
try:
    os.makedirs(config['output-dir'])
except FileExistsError:
    log(_error("Output dir"), _path(config['output-dir']),
        _error("exists, and we're not confident enough yet to clear it :/"))
    sys.exit(1)

# Grab compile-time data
vars = {}
vars['time'] = strftime('%Y-%m-%dT%H:%M:%S%z')
try:
    vars['version'] = (check_output(['git', 'describe', '--tags'])
                       .decode().strip())
except CalledProcessError:
    pass
vars['pandoc-version'] = pandoc_version()

# Construct the menu?
pass

with TemporaryDirectory() as staging_dir:
    # Get source files from git repositories
    for dest_dir, info in config['gits'].items():
        # chdir to a new temp directory and clone the Git repo
        with chdir_temp() as tempdir:
            clone_dir = os.path.basename(dest_dir.rstrip('/'))
            log(_action("Cloning"), _name(clone_dir))
            check_call(['git', 'clone', info['url'], clone_dir])
            for file in glob.iglob(os.path.join(clone_dir, '*.md')):
                log(_action("Adding"), _path(file))
                p = shutil.copy(file, staging_dir)
                basename = os.path.splitext(os.path.basename(p))[0] + '.html'
                dest_name = os.path.join(dest_dir, basename)
                config['pages'][dest_name] = {'source': p}

    # Compile pages
    for name, info in config['pages'].items():
        output_path = os.path.join(config['output-dir'], name.lstrip('/'))
        args = ['pandoc', '--to=html5', '--standalone',
                '--highlight-style=tango',
                '--template={}'.format(config['template']),
                '--output={}'.format(output_path)]
        if info.get('toc', False):
            args.append('--toc')
        for header in listify(info.get('header', [])):
            args.extend(['-H', header])
        for var, value in vars.items():
            args.extend(['-V', '{}={}'.format(var, value)])
        args.extend(listify(info.get('source', [])))
        log(_action("Compiling"), _name(output_path))
        # Create subdirs if needed
        subdirs = os.path.dirname(name).lstrip('/')
        if subdirs:
            os.makedirs(os.path.join(config['output-dir'], subdirs),
                        exist_ok=True)
        try:
            check_call(args)
        except CalledProcessError:
            log(_error("Failed:"), _name(output_path))

# Copy static files
for source, dest in config.get('copy', {}).items():
    dest_path = os.path.join(config['output-dir'], dest)
    log(_action("Copying"), _path(source), "->", _path(dest_path))
    shutil.copytree(source, dest_path)
