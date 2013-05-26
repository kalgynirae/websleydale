**Websleydale** is a Python 3 program that builds your website by compiling source
files with [Pandoc][pandoc]. All you have to do is write a simple YAML
configuration file. (…and figure out how to install Pandoc. …and PyYAML.)

# Usage

1.  Author your website pages in [Pandoc's markdown format][pandoc-markdown].

2.  Write a `config.yaml` in the root of your source directory that maps URLs
    to their source files. See the sample below.

3.  Run Websleydale:

        $ python3 websleydale.py -s . -o build

    This tells Websleydale that `config.yaml` is in the current directory
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

```yaml
%YAML 1.2
---
copy:
  css: css
  font: font
  image: image
  music: music/files
template: templates/lumeh.html
menu: !!omap
  - index: /index.html
  - music: /music.html
  - projects: /projects/
  - recipes: /recipes/
  - wiki: /wiki/
  - chorus: /chorus/
  - MUTAP: /mutap/
pages:
  index.html:
    source: pages/index.pd
  music.html:
    source: pages/music.pd
  boxer.html:
    source: pages/boxer.pd
  jabberwockus.html:
    source: pages/jabberwockus.pd
  krypto.html:
    source: pages/krypto.pd
    header: pages/krypto.header
  wiki:
    dragee.html:
      source: pages/wiki/dragee.pd
    early-twenty-first-century.html:
      source: pages/wiki/early-twenty-first-century.pd
  games:
    narchanso.html:
      source: pages/games/narchanso.pd
      toc: yes
    the-base-game.html:
      source: pages/games/the-base-game.pd
      toc: yes
  recipes: !github
    repo: kalgynirae/recipes
    index.html:
      source: README.md
    chili.html:
      source: chili.pd
    cookies.html:
      source: cookies.pd
    creme_brulee_cheesecake.html:
      source: creme_brulee_cheesecake.pd
    curry.html:
      source: curry.pd
    krishna_dressing.html:
      source: krishna_dressing.pd
    sweet_potato_casserole.html:
      source: sweet_potato_casserole.pd
  projects:
    index.html:
      source: pages/projects_index.html
    think-green: !github
      repo: kalgynirae/thinking-green
      index.html:
        source: README
    mideast-sidearm-hideaway: !github
      repo: kalgynirae/mideast-sidearm-hideaway
      index.html:
        source: README.md
        toc: yes
    websleydale: !github
      repo: kalgynirae/websleydale
      index.html:
        source: README.md
    routemaster: !github
      repo: routemaster/routemaster-frontend
      index.html:
        source: README.md
        toc: yes
    golfram-alpha: !github
      repo: kalgynirae/Golfram-Alpha
      index.html:
        source: README
  testing:
    narchanso-twice.html:
      source: [pages/games/narchanso.pd, pages/games/narchanso.pd]
      toc: yes
```

[pandoc]: http://www.johnmacfarlane.net/pandoc/
[pandoc-markdown]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
[lumeh.org]: http://lumeh.org/
