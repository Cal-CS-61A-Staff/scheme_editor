import os


def get_scm_files():
    files = filter(lambda x: x.lower().endswith(".scm"), os.listdir(os.curdir))
    return [*files]
