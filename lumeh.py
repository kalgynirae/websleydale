from websleydale import build
from websleydale.handlers import index, pandoc
from websleydale.sources import Dir, Git

local = Dir("/home/lumpy/www/lumeh-new/pages")
recipes = Git("https://github.com/kalgynirae/recipes.git")
rockuefort = Git("https://github.com/kalgynirae/rockuefort.git")
routemaster = Git("https://github.com/routemaster/routemaster-frontend.git")
subjunctive = Git("https://github.com/kalgynirae/subjunctive.git")
think_green = Git("https://github.com/kalgynirae/thinking-green.git")
websleydale_ = Git("https://github.com/kalgynirae/websleydale.git")

menu = [
    ("index", "/"),
    ("music", "/music.html"),
    ("projects", "/projects/"),
    ("recipes", "/recipes/"),
    ("wiki", "/wiki/"),
    ("café", "/cafe/"),
    ("chorus", "/chorus/"),
    ("MUTAP", "/mutap/"),
]

redirects = {
    "/games/narchanso.html": "/wiki/narchanso-ball.html",
}

tree = {
    "robots.txt": local["robots.txt"],
    "index.html": pandoc(local["index.pd"]),
    "music.html": pandoc(local["music.pd"]),
    "boxer.html": pandoc(local["boxer.pd"]),
    "jabbrwockus.html": pandoc(local["jabberwockus.pd"]),
    "krypto.html": pandoc(local["krypto.pd"], header="krypto.header"),
    "cafe": {
        "index.html": local["cafe/index.html"],
    },
    "recipes": recipes.auto(),
    "projects": index({
        "rockuefort/index.html": pandoc(rockuefort["README.md"]),
        "routemaster/index.html": pandoc(routemaster["README.md"], toc=True),
        "subjunctive/index.html": pandoc(subjunctive["README.md"]),
        "think-green/index.html": pandoc(think_green["README.md"]),
        "websleydale/index.html": pandoc(websleydale_["README.md"]),
    }),
    "wiki": local.auto("wiki"),
}

build("out", tree)
