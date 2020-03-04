**Websleydale** is a Python 3 program that builds your website by
compiling source files very quickly.

# Setup

1. Install `pipenv` (if you don't have it already).
2. Clone this repo and `cd` into it.
3. Run `pipenv sync` to create the virtualenv and install dependencies.
4. Place a symlink to `wb` somewhere on your path. (e.g., `ln -s --relative wb
   ~/bin/`).

# Project Configuration

You have to create a `websleydalerc.py` file in your project's root directory.
See <https://github.com/kalgynirae/lumeh.org/blob/master/websleydalerc.py> as an
example.
