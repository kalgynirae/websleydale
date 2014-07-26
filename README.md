**Websleydale** is a Python 3 program that builds your website by
compiling source files with [Pandoc].

# Prerequisites

*   [Pandoc] – installed and on your PATH so it can be run at the
    command line by typing `pandoc`

# Usage

1.  Author your website pages in [Pandoc's markdown format][pandoc-markdown].

2.  Write a `websleydale.py` script in the root of your project directory
    that maps output filenames to their sources. See the sample below.

3.  Make a template file. Pandoc uses a template to convert your
    Pandoc-markdown files to HTML. See the [Pandoc
    docs](http://www.johnmacfarlane.net/pandoc/README.html#templates)
    for more details. You can start with the [Pandoc's default HTML5
    template](https://github.com/jgm/pandoc-templates/blob/master/default.html5).

4.  Run `wb` (Websleydale build):

        $ wb path/to/project

    Websleydale will load the `websleydale.py` file from the directory
    you specify.
    (`.`) and that all output should go into the `build` directory.
    Websleydale defaults to using the current directory as the source
    directory but provides the `-s` flag to specify a different directory.

## Sample websleydalerc.py file

This is the configuration I'm using for [lumeh.org].

```python3
from websleydale import build, copy, directory, menu, pandoc, set_defaults
from websleydale.sources import Dir, Git

local = Dir(".")
pages = Dir("pages")
recipes = Git("https://github.com/kalgynirae/recipes.git")
rockuefort = Git("https://github.com/kalgynirae/rockuefort.git")
routemaster = Git("https://github.com/routemaster/routemaster-frontend.git")
subjunctive = Git("https://github.com/kalgynirae/subjunctive.git")
think_green = Git("https://github.com/kalgynirae/thinking-green.git")
websleydale_ = Git("https://github.com/kalgynirae/websleydale.git")

root = directory({
    "css": local["css"],
    "font": local["font"],
    "image": local["image"],
    "robots.txt": pages["robots.txt"],
    "index.html": pandoc(pages["index.pd"]),
    "music.html": pandoc(pages["music.pd"]),
    "boxer.html": pandoc(pages["boxer.pd"]),
    "jabbrwockus.html": pandoc(pages["jabberwockus.pd"]),
    "krypto.html": pandoc(pages["krypto.pd"], header=pages["krypto.header"]),
    "cafe": directory({
        "index.html": pages["cafe/index.html"],
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
    ("chorus", "/chorus/"),
    ("MUTAP", "/mutap/"),
])

#redirects = {
#    "/games/narchanso.html": "/wiki/narchanso-ball.html",
#    "/recipes/mung_bean_dahl.html": "/recipes/mung_bean_dal.html",
#}

set_defaults(
    menu=menu_,
    template=local["templates/lumeh.html"],
)

build("out", root)
```

[pandoc]: http://www.johnmacfarlane.net/pandoc/
[pyyaml]: http://pyyaml.org/
[docopt]: http://docopt.org/
[pandoc-markdown]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
[lumeh.org]: http://lumeh.org/
