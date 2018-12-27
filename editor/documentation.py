import json


def get_items():
    with open("editor/documentation.json") as f:
        data = json.load(f)
    out = []
    for elem in data["special forms"]:
        out.append(elem["name"])
    return set(out)


def export_items():
    items = get_items()
    out = []
    for i, v in enumerate(items):
        out.append({"id": i + 1, "text": v})
    return out
