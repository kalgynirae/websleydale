import os
import sys

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
    print('\u25b6', end=' ', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)

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
