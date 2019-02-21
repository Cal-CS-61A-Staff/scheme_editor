from scheme_runner import SchemeTestCase, Query


def out(*expected):
    return {"out": ["\n".join(expected) + "\n"]}


cases = [
    SchemeTestCase([Query("10", out("10"))]),
    SchemeTestCase([Query("(+ 137 349)", out("486"))]),
    SchemeTestCase([Query("(- 1000 334)", out("666"))]),

]
