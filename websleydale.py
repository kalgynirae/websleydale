#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from shlex import quote
from subprocess import PIPE
from typing import (
    Any,
    Awaitable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Union,
)

import jinja2
import yaml
from mistletoe import Document, HTMLRenderer

__version__ = "3.0-dev"

logger = logging.getLogger(__name__)
jinjaenv = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=True,
)


@dataclass
class Result:
    source_path: Path


@dataclass
class Site:
    known_authors: Set[Author]
    name: str
    repo_name: str
    repo_url: str
    tree: Dict[str, FileProducer]
    generator: str = "websleydale"
    time: datetime = datetime.now()


def build(site: Site, *, dest: str) -> None:
    destdir = Path(dest)
    if destdir.exists():
        logger.debug("Removing dest directory %s", destdir)
        shutil.rmtree(destdir)

    awaitables = []
    for pathstr, producer in site.tree.items():
        if not pathstr.startswith("/"):
            raise ValueError(f"Invalid path {pathstr!r} (doesn't start with '/')")
        if not isinstance(producer, FileProducer):
            raise TypeError(
                f"item for path {pathstr!r} has invalid type {type(producer)}"
            )
        awaitables.append(producer.run(destdir, pathstr, site))

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


class FileProducer:
    async def run(self, destdir: Path, path: str, site: Site) -> Result:
        ...


class file(FileProducer):
    def __init__(self, infile: Path) -> None:
        self.infile = infile

    async def run(self, destdir: Path, path: str, site: Site) -> Result:
        dest = destdir / path.lstrip("/")
        dest.parent.mkdir(exist_ok=True, parents=True)
        logger.debug("[%s] Copying file", self.infile)
        shutil.copy(self.infile, dest)
        return Result(self.infile)


class directory(FileProducer):
    def __init__(self, indir: Path) -> None:
        self.indir = indir

    async def run(self, destdir: Path, path: str, site: Site) -> Result:
        dest = destdir / path.lstrip("/")
        if dest.suffix != "":
            raise ValueError(f"Expected dest with no extension, got {dest!r}")
        dest.parent.mkdir(exist_ok=True, parents=True)
        logger.debug("[%s] Copying directory", self.indir)
        shutil.copytree(self.indir, dest, copy_function=shutil.copy)
        return Result(self.indir)


@dataclass(frozen=True)
class Author:
    display_name: str
    email: str
    url: Optional[str]


@dataclass
class GitFileInfo:
    authors: List[Author]
    repo_source_path: str
    repo_url: Optional[str]
    updated_date: datetime


async def _git_file_info(file: Path, site: Site) -> GitFileInfo:
    stdout, stderr, exitcode = await _run(
        [
            "bash",
            "-c",
            "--",
            f"cd {quote(str(file.parent))} && git ls-files --full-name {quote(str(file.name))} && git remote -v",
        ]
    )
    if stderr:
        for line in stderr.decode(errors="replace").splitlines():
            logger.debug("[%s] stderr: %s", file, line)
    lines = iter(stdout.decode(errors="replace").splitlines())
    repo_source_path = next(lines)
    repo_url = None
    for line in lines:
        remote_name, remote_url, _ = line.split(maxsplit=2)
        if remote_name == "origin":
            repo_url = remote_url
            break
    if repo_url is not None:
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-len(".git")]
        if repo_url.startswith("git@github.com:"):
            repo_name = repo_url[len("git@github.com:"):]
            repo_url = f"https://github.com/{repo_name}"

    stdout, stderr, exitcode = await _run(
        ["git", "log", "--format=%cI %ae %an", "--", str(file)]
    )
    if stderr:
        for line in stderr.decode(errors="replace").splitlines():
            logger.debug("[%s] stderr: %s", file, line)

    date = None
    for line in stdout.decode(errors="replace").splitlines():
        datestr, email, name = line.split(maxsplit=2)
        if date is None:
            date = datetime.fromisoformat(datestr)
        authors: Dict[Author, None] = {}
        author = next((a for a in site.known_authors if a.email == email), None)
        if author is None:
            author = Author(display_name=name, email=email, url=None)
        authors[author] = None
    assert date is not None
    return GitFileInfo(
        authors=list(authors.keys()),
        repo_source_path=repo_source_path,
        repo_url=repo_url,
        updated_date=date,
    )


class markdown(FileProducer):
    def __init__(self, infile: Path, template: str) -> None:
        self.infile = infile
        self.template = jinjaenv.get_template(template)

    async def run(self, destdir: Path, path: str, site: Site) -> Result:
        if path.endswith("/"):
            path += "index.html"
        elif path.endswith(".html"):
            pass
        else:
            raise ValueError(f"Expected dest ending in '/' or '.html', got {path!r}")

        dest = destdir / path.lstrip("/")
        dest.parent.mkdir(exist_ok=True, parents=True)

        logger.debug("[%s] Reading source", self.infile)
        text = self.infile.read_text()

        logger.debug("[%s] Loading Git info", self.infile)
        gitinfo = await _git_file_info(self.infile, site)
        pageinfo = {
            "authors": gitinfo.authors,
            "path": path,
            "repo_url": gitinfo.repo_url,
            "repo_source_path": gitinfo.repo_source_path,
            "source_path": str(self.infile),
            "updated_date": gitinfo.updated_date,
        }

        if text.startswith("---\n"):
            yamltext, text = text[4:].split("---\n", maxsplit=1)
            yamlinfo = yaml.safe_load(yamltext)
            pageinfo.update(yamlinfo)

        logger.debug("[%s] Rendering content", self.infile)
        with HTMLRenderer() as renderer:
            pageinfo["content"] = renderer.render(Document(text))

        logger.debug("[%s] Rendering template", self.infile)
        rendered = self.template.render(page=pageinfo, site=site)

        logger.debug("[%s] Writing to %s", self.infile, dest)
        dest.write_text(rendered)

        return Result(self.infile)


class sass(FileProducer):
    def __init__(self, infile: Path) -> None:
        self.infile = infile

    async def run(self, destdir: Path, path: str, site: Site) -> Result:
        dest = destdir / path.lstrip("/")
        if dest.suffix != ".css":
            raise ValueError(f"Expected dest ending in '.css', got {dest!r}")
        dest.parent.mkdir(exist_ok=True, parents=True)
        args = ["pysassc", str(self.infile), str(dest)]
        await _process_file(self.infile, args)
        return Result(self.infile)


async def _process_file(file: Path, args: List[str]) -> None:
    logger.debug("[%s] Running command: %s", file, " ".join(quote(arg) for arg in args))
    stdout, stderr, exitcode = await _run(args)
    if stdout:
        for line in stdout.decode(errors="replace").splitlines():
            logger.debug("[%s] stdout: %s", file, line)
    if stderr:
        for line in stderr.decode(errors="replace").splitlines():
            logger.debug("[%s] stderr: %s", file, line)
    logger.debug("[%s] Command returned %s", file, exitcode)


async def _run(args: List[str]) -> Tuple[bytes, bytes, int]:
    process = await asyncio.create_subprocess_exec(*args, stderr=PIPE, stdout=PIPE)
    stdout, stderr = await process.communicate()
    return stdout, stderr, process.returncode


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
