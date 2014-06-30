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

## Sample configuration file

This is the configuration I'm using for [lumeh.org]. Paths in the config file
are interpreted as relative to the source directory. The `copy` section says to
copy certain dirs into the output directory (e.g., `{source-dir}/music` copies
to `{output-dir}/music/files`). The template is simply passed to Pandoc. The
`menu` section defines a global site menu, the formatting of which is largely
tied to my template at the moment. The `pages` is the important part; it maps
URLs to their source file(s).

```python3
```

[pandoc]: http://www.johnmacfarlane.net/pandoc/
[pyyaml]: http://pyyaml.org/
[docopt]: http://docopt.org/
[pandoc-markdown]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
[lumeh.org]: http://lumeh.org/
