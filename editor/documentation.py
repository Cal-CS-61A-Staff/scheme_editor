import html
import json
from typing import List


def search(query: str):
    with open("editor/documentation.json") as f:
        data = json.load(f)
    out = []
    for elem in data["special forms"]:
        print(query in elem["name"])
        if query in elem["name"]:
            out.append(build(elem))
    print(data)
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

#
# def build_example(elem):
#     PREFIX = {
#         "comment": "; ",
#         "code": "scm> ",
#         "output": ""
#     }
#     return "\n".join(PREFIX[line["type"]] + line["val"] for line in elem)


def build_example(elem: List[str]):
    out = []
    for line in elem:
        if line.startswith("scm> ") or line.startswith(".... "):
            out.append("<pre>" + line + "</pre>")
        else:
            out.append(build_description(line))
    return "\n".join(out)


def build(elem):
    code = elem["form"]  # """(" + " ".join(build_code(e) for e in elem["form"]) + ")"
    description = build_description(elem["description"])
    # elem["form"] = code
    demo = build_example(elem["example"]) if "example" in elem else ""

    out = f"""
<h3><strong><code>{elem["name"]}</code></strong></h3>
<p>
<code>
    {escape(code)}
</code>
</p>
<p>
    {description}
</p>
"""
    if demo:
        out += f"""
<h6>For example:</h6>
{demo}
"""

    return out
