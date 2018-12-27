import html
import json


def search(query: str):
    with open("editor/documentation.json") as f:
        data = json.load(f)
    out = []
    for elem in data["special forms"]:
        print(query in elem["name"])
        if query in elem["name"]:
            out.append(build(elem))
    return out


def escape(val):
    return html.escape(val)


def build_code(elem):
    print(elem)
    if "group" in elem["qualifiers"]:
        return apply_qualifiers("(" + " ".join(build_code(e) for e in elem["contents"]) + ")", elem["qualifiers"])
    else:
        return apply_qualifiers(elem["val"], elem["qualifiers"])


def apply_qualifiers(elem, qualifiers):
    out = elem

    if "exact" in qualifiers:
        assert "symbol" in qualifiers
        return out

    if "optional" in qualifiers:
        out = "[" + out + "]"
    elif "group" not in qualifiers:
        out = "<" + out + ">"

    if "multiple" in qualifiers:
        out += " ..."

    return out


def build_description(elem):
    return escape(elem).replace(escape("<"), "<code>").replace(escape(">"), "</code>")


def build(elem):
    code = "(" + " ".join(build_code(e) for e in elem["form"]) + ")"
    description = build_description(elem["description"])

    escaped_demo = """
; assigns x to a lambda that takes in no arguments and returns 5
scm> (define x (lambda () 5))
; calls x, returning 5
scm> (x)
5"""
    return f"""
<h3><strong><code>{elem["name"]}</code></strong></h3>
<p>
<code>
    {escape(code)}
</code>
</p>
<p>
    {description}
</p>
<h6>For example:</h6>
<pre>{escaped_demo}</pre>
"""
