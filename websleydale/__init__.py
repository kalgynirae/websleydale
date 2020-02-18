#!/usr/bin/env python3
import asyncio
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable

from . import log, util

__all__ = ["build", "files", "markdown", "merge", "sass"]
__version__ = "3.0-dev"


def build(root: Awaitable, *, dest: str) -> None:
    destpath = Path(dest)
    if destpath.exists():
        shutil.rmtree(destpath)
    asyncio.run(copy(root, destpath))


@dataclass
class File:
    path: Path
    source_path: Path


class Processor:
    dest_extension: ClassVar[str]

    def __init__(self, source: File, dest: Path = None) -> None:
        self.source = source
        if dest is None:
            self.dest = util.temporary_file(self.dest_extension)
        else:
            self.dest = dest
        self._processed = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.source})"

    async def process(self) -> None:
        if self._processed:
            raise RuntimeError(r"Tried to process {self} more than once")
        self._processed = True


async def copy(file: File, dest: Path) -> None:
    dest.parent.mkdir(exist_ok=True, parents=True)
    log.debug("copy {} -> {}", file, dest)
    try:
        shutil.copy(file.path, dest)
    except IsADirectoryError:
        shutil.copytree(file.path, dest, copy_function=shutil.copy)


async def sass(file: File, dest: Path) -> None:
    args = [
        "pysassc",
        str(file.path),
        str(dest),
    ]
    await _process_file(file, args)


async def _process_file(file: File, args: List[str]) -> None:
    log.debug("[{}] Running command: {}", file, " ".join(quote(arg) for arg in args))
    process = await asyncio.create_subprocess_exec(
        *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stdout:
        for line in stdout.decode(errors="replace").splitlines():
            log.debug("[{}] stdout: {}", file, line)
    if stderr:
        for line in stderr.decode(errors="replace").splitlines():
            log.debug("[{}] stderr: {}", file, line)
    log.debug("[{}] Command returned {}", file, process.returncode)


class Dir:
    def __init__(self, path="."):
        self.directory = pathlib.Path(path)
        if not self.directory.is_dir():
            raise ValueError("not a directory: %s" % path)

    async def __getitem__(self, key):
        return SourceFile(self.directory / key)

    def __repr__(self):
        return "{}({!r})".format(self.__class__, str(self.directory))
