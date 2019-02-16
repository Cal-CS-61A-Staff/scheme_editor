from libraries import mistune


def search(query):
    with open("editor/scheme_documentation.md") as f:
        contents = str(f.read())
        return [mistune.markdown(contents)]


search("cond")
