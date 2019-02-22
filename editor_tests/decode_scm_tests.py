from scheme_runner import Query, SchemeTestCase


def balanced(code):
    return sum(x.count("(") - x.count(")") for x in code) == 0


def decode(filename: str):
    if not filename.endswith(".scm"):
        filename += ".scm"
    with open(filename) as f:
        contents = str(f.read())
        groups = {}
        curr_case = None
        for line in contents.split("\n"):
            line = line.strip()
            # if not line:
            #     if not curr_case or not curr_case.queries or not curr_case.queries[-1].code:
            #         continue
            #     most_recent_code = curr_case.queries[-1].code[-1]
            #     if most_recent_code.count("(") != most_recent_code.count(")"):
            #         # heuristic check for finished expressions
            #         continue
            #     curr_case.queries.append(Query(code=[], expected={}))
            # el

            if not line:
                continue
            elif line.startswith(";;; group>"):
                curr_case = SchemeTestCase([Query(code=[], expected={})])
                groups[line.split("group>", 1)[1]] = curr_case
            elif line.startswith(";"):
                if not line.startswith("; expect"):
                    continue  # useless comments
                expect_str = line.split("; expect")[1]
                curr_case.queries[-1].expected["out"] = \
                    [curr_case.queries[-1].expected.get("out", [""])[0]
                     + "".join(x.strip() + "\n" for x in expect_str.split(";"))]
            elif not balanced(curr_case.queries[-1].code):
                curr_case.queries[-1].code.append(line)
            else:
                curr_case.queries.append(Query([line], {}))

    print(groups)

    for group in groups:
        filename = f"scm_tests/case_{group.strip().lower().replace(' ', '-')}.py"

        with open(filename, "w") as f:
            f.write("")

        def write(x):
            print(x)
            with open(filename, "a") as f:
                f.write(x + "\n")

        write("from scheme_runner import SchemeTestCase, Query")
        write("cases = [")
        write(repr(groups[group]))
        write("]")


if __name__ == '__main__':
    print("# stdout is a viable test file")
    decode(input("# input filename: "))
