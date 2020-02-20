#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from shlex import quote
from subprocess import PIPE
from typing import Any, Awaitable, Dict, Iterable, List, Union

import jinja2
import yaml

from mistletoe import Document, HTMLRenderer

__version__ = "3.0-dev"

logger = logging.getLogger(__name__)
jinjaenv = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)


@dataclass
class Result:
    source_path: Path


@dataclass
class Site:
    name: str
    tree: Dict[Union[str, Path], FileProducer]


def build(site: Site, *, dest: str) -> None:
    destdir = Path(dest)
    if destdir.exists():
        logger.debug("Removing dest directory %s", destdir)
        shutil.rmtree(destdir)

    awaitables = []
    for path, producer in site.tree.items():
        if not isinstance(producer, FileProducer):
            raise TypeError(f"item for path {path!r} has invalid type {type(producer)}")
        awaitables.append(producer.run(destdir / path, make_info(site, Path(path))))

    results = asyncio.run(gather(awaitables))
    for result, path in zip(results, site.tree.keys()):
        if isinstance(result, Exception):
            logger.error(
                "[%s] %s: %s", path, result.__class__.__name__, result, exc_info=result
            )
        else:
            logger.debug("[%s] Success!", path)


async def gather(
    awaitables: Iterable[Awaitable[Result]],
) -> List[Union[Result, Exception]]:
    return await asyncio.gather(*awaitables, return_exceptions=True)


@dataclass
class PageInfo:
    site: Dict[str, Any]
    page: Dict[str, Any]
    time: datetime = datetime.now()


def make_info(site: Site, path: Path) -> PageInfo:
    return PageInfo(site={"name": site.name}, page={"path": path})


class FileProducer:
    async def run(self, dest: Path, info: PageInfo) -> Result:
        ...


class file(FileProducer):
    def __init__(self, infile: Path) -> None:
        self.infile = infile

    async def run(self, dest: Path, info: PageInfo) -> Result:
        dest.parent.mkdir(exist_ok=True, parents=True)
        logger.debug("[%s] Copying file", self.infile)
        shutil.copy(self.infile, dest)
        return Result(self.infile)


class directory(FileProducer):
    def __init__(self, indir: Path) -> None:
        self.indir = indir

    async def run(self, dest: Path, info: PageInfo) -> Result:
        dest.mkdir(exist_ok=True, parents=True)
        logger.debug("[%s] Copying directory", self.indir)
        shutil.copytree(self.indir, dest, copy_function=shutil.copy)
        return Result(self.indir)


class markdown(FileProducer):
    def __init__(self, infile: Path, template: str) -> None:
        self.infile = infile
        self.template = jinjaenv.get_template(template)

    async def run(self, dest: Path, info: PageInfo) -> Result:
        dest.parent.mkdir(exist_ok=True, parents=True)

        logger.debug("[%s] Reading source", self.infile)
        text = self.infile.read_text()

        if text.startswith("---\n"):
            yamltext, text = text[4:].split("---\n", maxsplit=1)
            yamlinfo = yaml.safe_load(yamltext)
            info.page.update(yamlinfo)

        logger.debug("[%s] Rendering content", self.infile)
        with HTMLRenderer() as renderer:
            info.page["content"] = renderer.render(Document(text))

        logger.debug("[%s] Rendering template", self.infile)
        rendered = self.template.render(**asdict(info))

        logger.debug("[%s] Writing to %s", self.infile, dest)
        dest.write_text(rendered)

        return Result(self.infile)


class sass(FileProducer):
    def __init__(self, infile: Path) -> None:
        self.infile = infile

    async def run(self, dest: Path, info: PageInfo) -> Result:
        dest.parent.mkdir(exist_ok=True, parents=True)
        args = [
            "pysassc",
            str(self.infile),
            str(dest),
        ]
        await _process_file(self.infile, args)
        return Result(self.infile)


async def _process_file(file: Path, args: List[str]) -> None:
    logger.debug("[%s] Running command: %s", file, " ".join(quote(arg) for arg in args))
    process = await asyncio.create_subprocess_exec(*args, stderr=PIPE, stdout=PIPE)
    stdout, stderr = await process.communicate()
    if stdout:
        for line in stdout.decode(errors="replace").splitlines():
            logger.debug("[%s] stdout: %s", file, line)
    if stderr:
        for line in stderr.decode(errors="replace").splitlines():
            logger.debug("[%s] stderr: %s", file, line)
    logger.debug("[%s] Command returned %s", file, process.returncode)


root = Path(".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="wb")
    parser.add_argument("rcfile", nargs="?", default="websleydalerc.py")
    parser.add_argument("--verbose", action="store_true", help="print lots of messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    logger.debug("exec(%r)", args.rcfile)
    with open(args.rcfile) as f:
        exec(f.read(), {})
