def decode(filename: str):
    if not filename.endswith(".scm"):
        filename += ".scm"
    with open(filename) as f:
        contents = str(f)
        tests = []
        for line in contents.split("\n"):
            if line.startswith(";"):
                if not line.startswith("; expect"):
                    continue  # useless comments
                tests[-1].append(line.split("; expect")[0])
            elif line:
                tests.append([line])
        print(tests)