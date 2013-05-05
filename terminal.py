prefix = '\x1b['
set_fg_color = '\x1b[3{}m'
set_bg_color = '\x1b[4{}m'
set_style = '\x1b[{}m'
color_names = 'black red green yellow blue magenta cyan white'.split()
colors = {color: index for index, color in enumerate(color_names)}
styles = {'bold': 1, 'underline': 4}
reset = '\x1b[0m'

def highlighter(color=None, bg_color=None, style=None):
    format_string = ((set_fg_color.format(colors[color]) if color else '') +
                     (set_bg_color.format(colors[bg_color]) if bg_color else '') +
                     (set_style.format(styles[style]) if style else '') +
                     '{}' + (reset if style or color else ''))
    def highlight(s):
        return format_string.format(s)
    return highlight

blue = highlighter(color='blue')
def log(*args, **kwargs):
    print(blue('>>'), *args, **kwargs)

_action = highlighter('yellow')
_error = highlighter('red')
_name = highlighter('green')
_path = highlighter('blue')
