from websleydale import build, files, markdown, merge, sass

root = merge(
    {"test.css": sass(files["styles/test.sass"])},
    {file.path: markdown(file) for file in files["pages/**/*.md"]},
)
build(root, dest="out")
