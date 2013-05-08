**Websleydale** is a Python 3 program that builds your website by compiling source
files with [Pandoc][pandoc]. All you have to do is write a simple YAML
configuration file. (…and figure out how to install Pandoc. …and PyYAML.)

## Usage

1.  Author your website pages in [Pandoc's markdown format][pandoc-markdown].

2.  Write a config file that maps your source files to their URLs. See the
    sample below.

3.  Run websleydale.

        $ python3 websleydale.py -c <your config file> -o <output directory>

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
  share/css: css
  share/font: font
  share/image: image
template: templates/lumeh.html
menu: !!omap
  - index: /index.html
  - music: /music.html
  - projects: /projects/
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
  games/narchanso.html:
    source: pages/narchanso.pd
    toc: yes
  projects/index.html:
    source: pages/projects.pd
  projects/think-green/index.html:
    source: https://raw.github.com/kalgynirae/thinking-green/master/README
  projects/recipes/cookies_summary.html:
    source: https://raw.github.com/kalgynirae/recipes/master/cookies_summary.html
  projects/mideast-sidearm-hideaway/index.html:
    source: https://raw.github.com/kalgynirae/mideast-sidearm-hideaway/master/README.md
  projects/websleydale/index.html:
    source: https://raw.github.com/kalgynirae/websleydale/master/README.md
  projects/routemaster/index.html:
    source: https://raw.github.com/routemaster/routemaster-frontend/master/README.md
  projects/golfram-alpha/index.html:
    source: https://raw.github.com/kalgynirae/Golfram-Alpha/master/README
```

[pandoc]: http://www.johnmacfarlane.net/pandoc/
[pandoc-markdown]: http://www.johnmacfarlane.net/pandoc/README.html#pandocs-markdown
