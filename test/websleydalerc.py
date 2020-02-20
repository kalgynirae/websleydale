from websleydale import Site, build, markdown, root, sass

site = Site(
    name="Test Site",
    tree={
        "test.css": sass(root / "styles/test.sass"),
        **{
            path.relative_to(root / "pages").with_suffix(".html"): markdown(
                path, template="page.html"
            )
            for path in root.glob("pages/**/*.md")
        },
    },
)
build(site, dest="out")
