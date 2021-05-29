from websleydale import (
    Author, Site, build, jinja, markdown, root, sass
)

site = Site(
    name="Websleydale Test Site",
    tree={
        "test.css": sass(root / "styles/test.sass"),
        **{
            str(path.relative_to(root / "pages").with_suffix(".html")): (
                jinja(markdown(path), template="page.html")
            )
            for path in root.glob("pages/**/*.md")
        },
    },
    repo_name="kalgynirae/websleydale",
    repo_url="https://github.com/kalgynirae/websleydale",
    known_authors={
        Author(
            display_name="kalgynirae",
            email="colinchan@lumeh.org",
            url="https://github.com/kalgynirae/",
        ),
    },
)
build(site, dest="out")
