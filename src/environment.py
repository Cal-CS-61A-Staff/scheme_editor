import src.execution as execution
from src.datamodel import Symbol, Nil, SingletonTrue, SingletonFalse
from src.evaluate_apply import Frame

print("importing environment")

def make_frame_decorator(defdict):
    def global_builtin(name):
        def decorator(cls):
            cls.__repr__ = lambda self: f"#[{name}]"
            defdict[Symbol(name)] = cls()
            return cls

        return decorator

    return global_builtin


defdict = {}
global_attr = make_frame_decorator(defdict)


def build_global_frame():
    from src import special_forms, primitives, gui
    primitives.load_primitives()
    frame = Frame("builtins")
    for k, v in defdict.items():
        frame.assign(k, v)
    frame.assign(Symbol("nil"), Nil)
    frame.assign(Symbol("#t"), SingletonTrue)
    frame.assign(Symbol("#f"), SingletonFalse)

    with open("src/builtins.scm") as file:
        execution.string_exec([" ".join(file.readlines())], lambda *x, **y: None, frame)

    return Frame("Global", frame)
