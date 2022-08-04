from typing import Callable, Generic, TypeVar

from py_monads.monad import Monad, a, b, kliesli_factory, KliesliT


class Maybe(Monad[a]):
    val: a = None


class Nothing(Maybe[a]):
    def __eq__(self, other):
        self.bind = bind
        return type(other) is Nothing

    def __mul__(self, other):
        return bind(self, other)


class Just(Maybe[a]):
    def __init__(self, val: a):
        self.bind = bind
        self.val: a = val

    def __eq__(self, other):
        if type(other) is not Just:
            return False
        return self.val == other.val


def unit(val: a) -> Just[a]:
    return Just(val)


def bind(ma: Maybe[a], k: KliesliT) -> Maybe[b]:
    if type(ma) is Nothing:
        return Nothing()
    else:
        try:
            val = ma.val
            return k(val)
        except Exception:
            return Nothing()


Kliesli = kliesli_factory(bind)


def bind_chain(ma: Maybe[a], *ks: KliesliT) -> Maybe[b]:
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
