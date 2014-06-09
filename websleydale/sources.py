#/usr/bin/env python3
import asyncio
import logging
import pathlib
import tempfile
from urllib.parse import urlsplit

from .util import log, _action, _error, _name, _path, _debug

class GitError(Exception):
    pass

class Dir:
    def __init__(self, path='.'):
        self.path = pathlib.Path(path)
        if not self.path.is_dir():
            raise ValueError("not a directory: %s" % path)

    def __getitem__(self, key):
        yield (self.path / key).open()

    def auto(self, path='.'):
        for path in (self.path / path).iterdir():
            yield path.open()

class Git(Dir):
    def __init__(self, clone_url, checkout='master', directory=None):
        self.checkout = checkout
        self.clone_url = clone_url
        if directory is None:
            self._temporary_directory = tempfile.TemporaryDirectory()
            self.directory = self._temporary_directory.name
        else:
            self.directory = directory
        if not clone_url.startswith('http'):
            raise ValueError("non-http clone url: %s" % clone_url)
        if 'github.com' in clone_url:
            self.host = "GitHub"
        elif 'bitbucket.org' in clone_url:
            self.host = "Bitbucket"
        else:
            self.host = urlsplit(clone_url).netloc
        self.web_url = clone_url.rstrip('.git')

    def __repr__(self):
        return '{}({!r}, checkout={!r})'.format(self.__class__, self.clone_url,
                                                self.checkout)

    @asyncio.coroutine
    def clone(self):
        log(_action("Cloning"), _name(self.clone_url))

        # git clone
        args = ['git', 'clone', '-q', self.clone_url, self.directory]
        process = yield from asyncio.create_subprocess_exec(
                *args)
        return_code = yield from process.wait()
        if return_code != 0:
            raise GitError("git clone returned %d" % return_code)

        # git checkout
        args = ['git', '-C', self.directory, 'checkout', '-q', self.checkout]
        process = yield from asyncio.create_subprocess_exec(
                *args, stderr=asyncio.subprocess.STDOUT)
        return_code = yield from process.wait()
        if return_code != 0:
            raise GitError("git checkout returned %d" % return_code)

        # git log
        args = ['git', '-C', self.directory, 'log', '-n', '1',
                '--pretty=format:%h']
        process = yield from asyncio.create_subprocess_exec(
                *args, stderr=asyncio.subprocess.STDOUT,
                stdout=asyncio.subprocess.PIPE)
        output, _ = yield from process.communicate()
        self.version = output.decode().strip()
        log(_action("Checked out"), _name(self.version),
            _action("from"), _name(self.clone_url))
