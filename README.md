**Websleydale** is a Python 3 program that builds your website by compiling source
files with [Pandoc][pandoc]. All you have to do is write a simple YAML
configuration file. (…and figure out how to install Pandoc. …and PyYAML.)

## Usage

1.  Author your website pages in [Pandoc's markdown format][pandoc-markdown].

2.  Write a `config.yaml` that maps your source files to their URLs. See the
    sample below.

3.  Run websleydale.

        $ python3 websleydale.py -o <output directory>

### Sample configuration file

This is the configuration I'm using for lumeh.org. Paths in the config file are
interpreted as relative to the config file (so if the config file is
`/foo/bar/config.yaml` then `pages/music.pd` means `/foo/bar/pages/music.pd`).
The `copy` section says to copy certain dirs into the output directory (e.g.,
`/foo/bar/share/css` copies to `/foo/bar/output/css` if `/foo/bar/output` is
the output directory). The template is simply passed to Pandoc. The `menu`
section is largely tied to my template at the moment. The `pages` is the
important part; it maps URLs to their source file(s).

```yaml
%YAML 1.2
---
copy:
  css: css
  font: font
  image: image
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
  narchanso-twice.html:
    source: [pages/narchanso.pd, pages/narchanso.pd]
    toc: yes
  games:
    narchanso.html:
      source: pages/narchanso.pd
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
```

[pandoc]: http://www.johnmacfarlane.net/pandoc/
[pandoc-markdown]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
