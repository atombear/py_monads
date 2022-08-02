from typing import Any, Callable

class Maybe:
    pass


class Nothing(Maybe):
    def __eq__(self, other):
        return type(other) is Nothing
    def __mul__(self, other):
        return bind(self, other)


class Just(Maybe):
    def __init__(self, val: Any):
        self.val: Any = val

    def __eq__(self, other):
        if type(other) is not Just:
            return False
        return self.val == other.val

    def __mul__(self, other):
        return bind(self, other)


def unit(val: Any) -> Just:
    return Just(val)


def bind(ma: Maybe, f: Callable[[Any], Maybe]) -> Maybe:
    if type(ma) is Nothing:
        return Nothing()
    else:
        try:
            val = ma.val
            return f(val)
        except Exception:
            return Nothing()


def bind_chain(ma: Maybe, *fs: Callable[[Any], Maybe]) -> Maybe:
    ret = ma
    for f in fs:
        ret = bind(ret, f)
    return ret


if __name__ == '__main__':
    assert bind(Just(3), lambda x: Just(x+5)) == Just(8)
    assert bind(
                bind(Just(3),
                     lambda x: Just(x + 5)),
                lambda x: Just(x * 3)) == Just(24)
    
    assert bind_chain(Just(7),
                      lambda x: Just(x + 10),
                      lambda x: Just(x * 3),
                      lambda x: Just(x - 11)) == Just(40)

    assert bind_chain(Just(1),
                      lambda x: Just(x / 0),
                      lambda x: Just(x + 3)) == Nothing()

    assert (Just(12)
            * (lambda x: Just(x + 10)
            * (lambda x: Just(x * 3)))) == Just(66)
