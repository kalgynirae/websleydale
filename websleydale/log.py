import pathlib
import sys

_color = True
_log_file = sys.stderr
_debug = True
_verbose = True

def _c(test, color, bg_color=None, style=None, conv=str):
    return test, color, bg_color, style, conv

_color_rules = [
    _c(lambda x: isinstance(x, pathlib.Path), 'blue'),
    _c(lambda x: str(x).startswith('http'), 'cyan'),
    _c(lambda x: str(x).startswith('warning'), 'red'),
    _c(lambda x: str(x).startswith('debug'), 'yellow'),
    _c(lambda x: not isinstance(x, str), 'green'),
]

_COLOR_NAMES = 'black red green yellow blue magenta cyan white'.split()
_COLORS = {color: index for index, color in enumerate(_COLOR_NAMES)}
_RESET = '\x1b[0m'
_SET_BG_COLOR = '\x1b[4%sm'
_SET_FG_COLOR = '\x1b[3%sm'
_SET_STYLE = '\x1b[%sm'
_STYLES = {'bold': 1, 'underline': 4}
def colorize(obj):
    for test, color, bg_color, style, conv in _color_rules:
        if test(obj):
            if color:
                q = ((_SET_FG_COLOR % _COLORS[color] if color else '') +
                     (_SET_BG_COLOR % _COLORS[bg_color] if bg_color else '') +
                     (_SET_STYLE % _STYLES[style] if style else '') +
                     '{}' + (_RESET if color or bg_color or style else ''))
            return q.format(conv(obj))
    else:
        return obj

def format(message, *args):
    return colorize(message).format(*map(colorize, args))

def _loginate_it_up(message):
    print(message, file=_log_file)

def debug(message, *args):
    if _debug:
        _loginate_it_up(format("debug: " + message, *args))

def info(message, *args):
    if _verbose:
        _loginate_it_up(format(message, *args))

def warning(message, *args):
    _loginate_it_up(format("warning: " + message, *args))
