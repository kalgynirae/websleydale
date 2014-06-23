#/usr/bin/env python3
import asyncio
import logging
import pathlib
from urllib.parse import urlsplit

from . import log
from .handlers import pandoc
from .util import temporary_dir

class GitError(Exception):
    pass

class Dir:
    def __init__(self, path='.'):
        self.directory = pathlib.Path(path)
        if not self.directory.is_dir():
            raise ValueError("not a directory: %s" % path)

    def __getitem__(self, key):
        yield from asyncio.sleep(0)
        return self.directory / key

    def __repr__(self):
        return '{}({!r})'.format(self.__class__, str(self.directory))

    def auto(self, path='.'):
        return {p: pandoc(self[p]) for p in (self.directory / path).iterdir()}

class Git:
    def __init__(self, clone_url, checkout=None, directory=None):
        self.checkout = checkout
        self.clone_url = clone_url
        if directory is None:
            t = temporary_dir(clone_url.split('/')[-1])
            self.directory = pathlib.Path(t)
        else:
            self.directory = pathlib.Path(directory)
        if not clone_url.startswith('http'):
            raise ValueError("non-http clone url: %s" % clone_url)
        if 'github.com' in clone_url:
            self.host = "GitHub"
        elif 'bitbucket.org' in clone_url:
            self.host = "Bitbucket"
        else:
            self.host = urlsplit(clone_url).netloc
        self.web_url = clone_url.rstrip('.git')
        self.clone_finished = asyncio.Task(self._clone())

    @asyncio.coroutine
    def __getitem__(self, key):
        yield from self.clone_finished
        return self.directory / key

    def __repr__(self):
        return '{}({!r}, checkout={!r})'.format(self.__class__, self.clone_url,
                                                self.checkout)

    def auto(self, path='.'):
        log.warning("Git.auto() is broken")
        # The directory is still empty when the iterdir() happens
        return {p: pandoc(self[p]) for p in (self.directory / path).iterdir()}

    @asyncio.coroutine
    def _clone(self):
        log.info("Cloning {}", self.clone_url)

        # git clone
        args = ['git', 'clone', '-q', self.clone_url, str(self.directory)]
        process = yield from asyncio.create_subprocess_exec(
                *args, stderr=asyncio.subprocess.PIPE)
        _, stderr = yield from process.communicate()
        return_code = yield from process.wait()
        if return_code != 0:
            print(stderr, file=sys.stderr)
            raise GitError("git clone returned %d" % return_code)

        # git checkout
        if self.checkout is not None:
            args = ['git', '-C', str(self.directory), 'checkout', '-q',
                    self.checkout]
            process = yield from asyncio.create_subprocess_exec(
                    *args, stderr=asyncio.subprocess.PIPE)
            _, stderr = yield from process.communicate()
            return_code = yield from process.wait()
            if return_code != 0:
                print(stderr, file=sys.stderr)
                raise GitError("git checkout returned %d" % return_code)

        # git log
        args = ['git', '-C', str(self.directory), 'log', '-n', '1',
                '--pretty=format:%h']
        process = yield from asyncio.create_subprocess_exec(
                *args, stderr=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE)
        output, _ = yield from process.communicate()
        self.version = output.decode().strip()
        log.info("Checked out {} from {}", self.version, self.clone_url)