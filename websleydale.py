#!/usr/bin/python3
"""Websleydale compiles your web site from a bunch of source files.

Usage: websleydale [-chv] [-s <dir>] -o <dir>

Options:
  -s <dir>, --source <dir>      Source directory [default: .]
  -o <dir>, --output <dir>      Output direcgtory [default: ./build]
  -c, --copy-only               Only copy static files
  -h, --help                    Show this message
  -v, --version                 Print the version
"""
__version__ = "1.1"

import contextlib
import os
from os.path import abspath, basename, dirname, join
import shutil
import subprocess
import sys
import tempfile
import time

from docopt import docopt
import yaml

class Github(dict):
    """Special dict for representing Github repositories"""
    @classmethod
    def construct(cls, loader, node):
        d = loader.construct_mapping(node)
        return cls(d)
yaml.add_constructor('!github', Github.construct)

@contextlib.contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)

def git_repo_version(repo_path):
    try:
        with chdir(repo_path):
            version = (subprocess.check_output(['git', 'describe', '--tags'])
                       .decode().strip())
    except subprocess.CalledProcessError:
        version = None
    return version

def github_clone_url(repo):
    return 'https://github.com/{}.git'.format(repo)

def github_web_url(repo):
    return 'https://github.com/{}'.format(repo)

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
_action = highlighter('yellow')
_error = highlighter('red')
_name = highlighter('green')
_path = highlighter('blue')
_debug = highlighter('cyan')

def listify(item):
    return item if isinstance(item, list) else [item]

def log(*args, **kwargs):
    print('\u25b6', end=' ')
    print(*args, **kwargs)

def mkdir_if_needed(path):
    try:
        os.makedirs(path, exist_ok=True)
    except FileExistsError as e:
        if e.errno == 17:
            # 17 means the permissions are abnormal, but we don't care
            pass
        else:
            raise

def pandoc_version():
    output = subprocess.check_output(['pandoc', '-v']).decode()
    return output.split('\n')[0].split()[1]

def parse_pages(config, base_path='', github_repo=None):
    githubs = []
    pages = []
    for path, config in config.items():
        if 'source' in config:
            # config is a dict for a page
            page = {'github-repo': False, 'header': [], 'source': [],
                    'toc': False}
            for key in page:
                if key == 'source':
                    page['source'].extend(listify(config['source']))
                else:
                    try:
                        page[key] = config[key]
                    except KeyError:
                        pass
            page['github-repo'] = github_repo
            page['path'] = join(base_path, path)
            pages.append(page)
        elif isinstance(config, Github):
            if github_repo:
                raise ValueError("Nested Github repos are not supported")
            # config is a dict for a Github repo
            github = {'branch': 'master', 'repo': None}
            for key in github:
                try:
                    github[key] = config[key]
                except KeyError:
                    pass
                else:
                    del config[key]
            github['path'] = join(base_path, path)
            githubs.append(github)
            _pages, _ = parse_pages(config, github['path'], github['repo'])
            pages.extend(_pages)
        else:
            # config is a dict for a subdir containing pages and/or githubs
            _pages, _githubs = parse_pages(config, join(base_path, path))
            pages.extend(_pages)
            githubs.extend(_githubs)
    return pages, githubs

def main():
    arguments = docopt(__doc__, version=__version__)

    # Load the configuration
    config_path = join(arguments['--source'], 'config.yaml')
    log(_action("Loading"), _path(config_path))
    with open(config_path) as f:
        config = yaml.load(f)
    pages, githubs = parse_pages(config['pages'])

    SOURCE_DIR = arguments['--source']
    if SOURCE_DIR == '.':
        SOURCE_DIR = ''
    OUTPUT_DIR = arguments['--output']

    # Create the output and staging directories if needed
    mkdir_if_needed(OUTPUT_DIR)

    # Grab compile-time data
    vars = {}
    vars['time'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    vars['pandoc-version'] = pandoc_version()
    vars['websleydale-version'] = __version__
    source_version = git_repo_version(SOURCE_DIR or '.')
    if source_version:
        vars['source-version'] = source_version

    if not arguments.get('--copy-only', False):
        with tempfile.TemporaryDirectory() as tempdir:

            # Clone githubs
            for github in githubs:
                log(_action("Cloning"), _name(github['repo']))
                args = ['git', 'clone', '--depth', '1', '--branch',
                        github['branch'], github_clone_url(github['repo']),
                        join(tempdir, github['repo'])]
                try:
                    subprocess.check_call(args)
                except subprocess.CalledProcessError:
                    log(_error("Clone failed:"), _name(github['repo']))

            # Compile pages
            for page in pages:
                template = join(SOURCE_DIR, config['template'])
                args = ['pandoc', '--to=html5', '--standalone',
                        '--highlight-style=tango',
                        '--template={}'.format(template),
                        '--output={}'.format(join(OUTPUT_DIR, page['path']))]
                if page['toc']:
                    args.append('--toc')
                for header in listify(page.get('header', [])):
                    args.extend(['-H', join(SOURCE_DIR, header)])
                for key, value in vars.items():
                    args.extend(['-V', '{}={}'.format(key, value)])
                if page['github-repo']:
                    url = github_web_url(page['github-repo'])
                    args.extend(['-V', 'github={}'.format(page['github-repo']),
                                 '-V', 'github-url={}'.format(url)])

                # Construct the menu
                menu_items = []
                for item_name, item_url in config['menu']:
                    active = (' class="active"'
                              if item_url == basename(page['path']) else '')
                    i = '<li><a href="{item_url}"{active}>{item_name}</a></li>'
                    menu_items.append(i.format(**locals()))
                args.extend(['-V',
                             'menu={}'.format('<!--\n-->'.join(menu_items))])

                # Build list of sources
                for source in page['source']:
                    if source.startswith('http'):
                        # Download the file and append the downloaded path
                        log(_action("Fetching"), _path(source))
                        subprocess.check_call(['curl', '-OsS', source])
                        args.append(join(tempdir, basename(source)))
                    elif page['github-repo']:
                        args.append(join(tempdir, page['github-repo'], source))
                    else:
                        args.append(join(SOURCE_DIR, source))

                # Create subdirs if needed
                subdirs = join(OUTPUT_DIR, dirname(page['path']))
                if subdirs:
                    mkdir_if_needed(subdirs)

                # Build the page
                log(_action("Building"), _name(page['path']))
                try:
                    subprocess.check_call(args)
                except subprocess.CalledProcessError:
                    log(_error("Failed:"), _name(page['path']))

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
