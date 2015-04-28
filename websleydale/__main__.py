import argparse

from . import log

parser = argparse.ArgumentParser(prog='wb')
parser.add_argument('rc_file', help=argparse.SUPPRESS)
parser.add_argument('--verbose', action='store_true', help='print lots of messages')
args = parser.parse_args()
log.configure(verbose=args.verbose)

log.debug('exec({!r})', args.rc_file)
with open(args.rc_file) as rc_file:
    globals = {}
    exec(rc_file.read(), globals)
