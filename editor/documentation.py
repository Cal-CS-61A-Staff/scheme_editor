import re

from libraries import mistune


def search(query):
    with open("editor/scheme_documentation.md") as f:
        query = query.strip().lower()

        contents = str(f.read())
        contents = re.sub(r"<a class='builtin-header' id='.*?'>\*\*(.*?)\*\*</a>", r"### **\1**", contents)

        divider = "##"
        elements = [divider + elem for elem in contents.split(divider)]
        elements = [elem for elem in elements if "\n" in elem.strip()]
        relevant_elems = []
        for elem in elements:
            if query in elem.lower():
                relevant_elems.append(elem)

        relevant_elems.sort(key=lambda x: 20 * x.split("\n")[0].count(query) / len(x.split("\n")[0]) + x.count(query) / len(x), reverse=True)
        return [mistune.markdown(elem) for elem in relevant_elems]
