import os


def get_scm_files():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    files = filter(lambda x: x.lower().endswith(".scm"), os.listdir(APP_ROOT))
    return [*files]


def save(code, filename):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    with open(APP_ROOT + "/" + filename, "w+") as file:
        file.truncate(0)
        file.seek(0)
        file.write("\n".join(code))
        file.flush()


def read_file(filename):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    with open(APP_ROOT + "/" + filename, "r") as file:
        return "".join([x for x in file])
