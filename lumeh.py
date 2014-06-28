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
    "/recipes/mung_bean_dahl.html": "/recipes/mung_bean_dal.html",
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
    "recipes": index({
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
    "projects": index({
        "rockuefort/index.html": pandoc(rockuefort["README.md"]),
        "routemaster/index.html": pandoc(routemaster["README.md"], toc=True),
        "subjunctive/index.html": pandoc(subjunctive["README.md"]),
        "think-green/index.html": pandoc(think_green["README.md"]),
        "websleydale/index.html": pandoc(websleydale_["README.md"]),
    }),
    "wiki": index({
        "%s.html" % name: pandoc(local["wiki/%s.pd" % name]) for name in [
            "dragee",
            "early-twenty-first-century",
        ]
    }),
}

build("out", tree)
