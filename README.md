**Websleydale** is a Python 3 program that builds your website by
compiling source files with [Pandoc].

# Prerequisites

*   [Pandoc] – installed and on your PATH as `pandoc`

# Installation

Clone this git repository and put the `wb` script on your PATH somehow.
For example, if you have `~/bin` in your PATH, you might do:

    $ git clone <clone url> && cd websleydale
    $ ln -s `pwd`/wb ~/bin/wb

# Usage

1.  Author your website pages in [Pandoc's markdown format].

2.  Make an HTML template file for Pandoc. You can use [Pandoc's default
    HTML5 template] as a starting point. See the [Pandoc docs] for more
    details.

3.  Write a `websleydalerc.py` script in the root dir of your project.
    See the sample below.

4.  Run `wb` (Websleydale build) from the root dir of your project.

        $ wb

    `wb` just executes the `websleydalerc.py` script with a little magic
    to make sure the `websleydale` Python package is on the Python path.

## Sample websleydalerc.py file

This is the configuration I'm using for [lumeh.org].

```python
from websleydale import build, copy, directory, menu, pandoc, set_defaults
from websleydale.sources import Dir, Git

local = Dir(".")
pages = Dir("pd")
htaccess = Dir("htaccess")
recipes = Git("https://github.com/kalgynirae/recipes.git")
rockuefort = Git("https://github.com/kalgynirae/rockuefort.git")
routemaster = Git("https://github.com/routemaster/routemaster-frontend.git")
subjunctive = Git("https://github.com/kalgynirae/subjunctive.git")
think_green = Git("https://github.com/kalgynirae/thinking-green.git")
websleydale_ = Git("https://github.com/kalgynirae/websleydale.git")

root = directory({
    ".htaccess": htaccess["root"],
    "files/.htaccess": htaccess["files"],
    "files/public/.htaccess": htaccess["files_public"],

    "css": local["css"],
    "font": local["font"],
    "image": local["image"],
    "media": local["media"],
    "favicon.ico": local["image/favicon.ico"],

    "robots.txt": pages["robots.txt"],
    "404.shtml": pandoc(pages["404.pd"]),
    "index.html": pandoc(pages["index.pd"]),
    "music.html": pandoc(pages["music.pd"]),
    "boxer.html": pandoc(pages["boxer.pd"]),
    "jabberwockus.html": pandoc(pages["jabberwockus.pd"]),
    "krypto.html": pandoc(pages["krypto.pd"], header=pages["krypto.header"]),
    "cafe": directory({
        "index.html": pandoc(pages["cafe/index.pd"]),
    }),
    "recipes": directory({
        "%s.html" % name: pandoc(recipes["%s.pd" % name]) for name in [
            "chili",
            "christmas_anything",
            "cookies",
            "creme_brulee_cheesecake",
            "curry",
            "krishna_dressing",
            "mung_bean_dal",
            "pumpkin_bread",
            "sugar_cookies",
            "sweet_potato_casserole",
        ]
    }),
    "projects": directory({
        "rockuefort/index.html": pandoc(rockuefort["README.md"]),
        "routemaster/index.html": pandoc(routemaster["README.md"], toc=True),
        "subjunctive/index.html": pandoc(subjunctive["README.md"]),
        "think-green/index.html": pandoc(think_green["README.md"]),
        "websleydale/index.html": pandoc(websleydale_["README.md"]),
    }),
    "wiki": directory({
        "%s.html" % name: pandoc(pages["wiki/%s.pd" % name]) for name in [
            "dragee",
            "early-twenty-first-century",
            "the-caring-continuum",
            "games/capture-the-flag",
            "games/narchanso",
            "games/the-base-game",
        ]
    }),
})

menu_ = menu([
    ("index", "/"),
    ("music", "/music.html"),
    ("projects", "/projects/"),
    ("recipes", "/recipes/"),
    ("wiki", "/wiki/"),
    ("café", "/cafe/"),
])

set_defaults(
    menu=menu_,
    template=local["templates/lumeh.html"],
)

build("out", root)
```

[Pandoc]: http://www.johnmacfarlane.net/pandoc/
[Pandoc's markdown format]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
[Pandoc's default HTML5 template]: https://github.com/jgm/pandoc-templates/blob/master/default.html5
[Pandoc docs]: http://www.johnmacfarlane.net/pandoc/README.html#templates
[lumeh.org]: http://lumeh.org/
