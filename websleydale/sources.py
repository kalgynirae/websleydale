import asyncio
import pathlib
from urllib.parse import urlsplit

from . import log
from .util import temporary_dir


class Dir:
    def __init__(self, path='.'):
        self.directory = pathlib.Path(path)
        if not self.directory.is_dir():
            raise ValueError("not a directory: %s" % path)

    def __getitem__(self, key):
        f = asyncio.Future()
        f.set_result(SourceFile(self.directory / key))
        return f

    def __repr__(self):
        return '{}({!r})'.format(self.__class__, str(self.directory))


class Git:
    def __init__(self, clone_url, checkout=None, directory=None):
        self.checkout = checkout
        self.clone_url = clone_url
        self.name = '/'.join(clone_url.split('/')[-2:])[:-len('.git')]
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
        info = self.generate_info(key)
        return SourceFile(self.directory / key, info)

    def __repr__(self):
        return '{}({!r}, checkout={!r})'.format(self.__class__, self.clone_url,
                                                self.checkout)

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
                '--pretty=format:%h %H']
        process = yield from asyncio.create_subprocess_exec(
                *args, stderr=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE)
        output, _ = yield from process.communicate()
        self.shorthash, self.hash = output.decode().strip().split()
        log.info("Checked out {} from {}", self.shorthash, self.clone_url)

    def generate_info(self, key):
        if self.host == 'GitHub':
            url = 'https://github.com/{name}/blob/{hash}/{key}'
        elif self.host == 'Bitbucket':
            url = 'https://bitbucket.org/{name}/src/{hash}/{key}'
        url = url.format(name=self.name, hash=self.hash, key=key)

        info = '<a href="{url}">{name}</a> on {host}'
        return info.format(host=self.host, url=url, name=self.name)


class GitError(Exception):
    pass


class SourceFile:
    def __init__(self, path, info=None):
        self.path = path
        self.info = info
