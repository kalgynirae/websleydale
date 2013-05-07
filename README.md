Websleydale is a Python 3 program that builds your website by compiling source
files with [Pandoc][pandoc].

Example configuration file:

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
