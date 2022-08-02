from typing import Callable, Generic, TypeVar

a = TypeVar('a')


class Monad(Generic[a]):
    pass


class Maybe(Monad[a]):
    pass


class Nothing(Maybe):
    def __eq__(self, other):
        return type(other) is Nothing
    def __mul__(self, other):
        return bind(self, other)


class Just(Maybe[a]):
    def __init__(self, val: a):
        self.val: a = val

    def __eq__(self, other):
        if type(other) is not Just:
            return False
        return self.val == other.val

    def __mul__(self, other):
        return bind(self, other)


class Kliesli:
    def __init__(self, f: Callable[[a], Monad[a]]):
        self.f = f

    def __mul__(self, other):
        """Associativity of monadic composition, eg m >>= f >>= g"""
        return Kliesli(lambda x: bind(self.f(x), other))


def unit(val: a) -> Just[a]:
    return Just(val)


def bind(ma: Maybe[a], k: Kliesli) -> Maybe[a]:
    if type(ma) is Nothing:
        return Nothing()
    else:
        try:
            val = ma.val
            return k.f(val)
        except Exception:
            return Nothing()


def bind_chain(ma: Maybe[a], *ks: Kliesli) -> Maybe[a]:
    ret = ma
    for k in ks:
        ret = bind(ret, k)
    return ret


if __name__ == '__main__':
    assert bind(Just(3), Kliesli(lambda x: Just(x+5))) == Just(8)
    assert bind(
                bind(Just(3),
                     Kliesli(lambda x: Just(x + 5))),
                Kliesli(lambda x: Just(x * 3))) == Just(24)
    
    assert bind_chain(Just(7),
                      Kliesli(lambda x: Just(x + 10)),
                      Kliesli(lambda x: Just(x * 3)),
                      Kliesli(lambda x: Just(x - 11))) == Just(40)

    assert bind_chain(Just(1),
                      Kliesli(lambda x: Just(x / 0)),
                      Kliesli(lambda x: Just(x + 3))) == Nothing()

    assert (Just(12)
            * Kliesli(lambda x: Just(x + 10)
            * Kliesli(lambda x: Just(x * 3)))) == Just(66)

    assert (Just(30) *
            (Kliesli(lambda x: Just(x / 10)) * Kliesli(lambda x: Just(x + 3)))) == Just(6.0)
