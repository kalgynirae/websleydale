**Websleydale** is the minimalist [static site generator] used to build
[lumeh.org]. Its feature set is limited to what lumeh.org requires, so
it is fairly minimal and runs very fast.

[static site generator]: https://en.wikipedia.org/wiki/Static_web_page
[lumeh.org]: https://lumeh.org/

**UPDATE (April 2025):** Websleydale has been moved into the [lumeh.org
repo]. This repository will no longer be updated.

[lumeh.org repo]: https://github.com/kalgynirae/lumeh.org

# Requirements

* Python 3.8 or later
* [pipenv] (for installing dependencies)

[pipenv]: https://docs.pipenv.org/

# Setup

1. Clone this repo and `cd` into it.
2. Run `pipenv sync` to create the virtualenv and install dependencies.
3. Place a symlink to the `wb` script somewhere in your PATH.
   (For example, if you already have a `~/bin` directory in your PATH,
   you can run `ln -s --relative wb ~/bin/` to create such a symlink.)

# Usage

First, create a `websleydalerc.py` file in your project's root directory
(see the example below).

Then, run `wb` in the same directory as the `websleydalerc.py` file
whenever you want to build your project.

## Example websleydalerc.py

Given the following source files:

```
.
├── index.md
├── memes/
│   └── loss.jpg
├── style.sass
└── templates/
    └── page.html
```

A corresponding `websleydalerc.py` might look like this:

```python
from websleydale import Site, build, dir, jinja, markdown, root, sass

site = Site(
    name="My Website",
    tree={
        # Process 'index.md' as Markdown and render it using the 'page.html'
        # Jinja template, and write the result as 'index.html' in the output dir
        "index.html": jinja(markdown(root / "index.md"), template="page.html"),

        # Process 'style.sass' as a Sass stylesheet and write the result as
        # 'style.css' in the output dir
        "style.css": sass(root / "style.sass"),

        # Copy all contents of the 'memes' directory into a directory called
        # 'memes' in the output dir
        "memes": dir(root / "memes"),
    },
)
build(site, dest="out")
```

For a full example, see [lumeh.org's config].

[lumeh.org's config]: https://github.com/kalgynirae/lumeh.org/blob/51ef1cf33045ab27dcb08a14b3b9ea3b437baf7a/websleydalerc.py
