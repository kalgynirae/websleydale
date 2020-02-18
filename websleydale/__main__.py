#!/usr/bin/env python3
import argparse
from pathlib import Path

from . import log

parser = argparse.ArgumentParser(prog="wb")
parser.add_argument("project-dir", help=argparse.SUPPRESS, type=Path)
parser.add_argument("--verbose", action="store_true", help="print lots of messages")
args = parser.parse_args()
log.configure(verbose=args.verbose)

rcfile = args.project_dir / "websleydalerc.py"
log.debug("exec({!r})", rcfile)
with open(rcfile) as f:
    exec(f.read(), {})
