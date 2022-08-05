from py_monads.monad import Monad, a, b, kleisli_factory, KleisliT


class Maybe(Monad[a]):
    val: a

    def __init__(self):
        self.bind = bind


class Nothing(Maybe[a]):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        return type(other) is Nothing


class Just(Maybe[a]):

    def __init__(self, val: a):
        super().__init__()
        self.val: a = val

    def __eq__(self, other):
        if type(other) is not Just:
            return False
        return self.val == other.val


def unit(val: a) -> Just[a]:
    return Just(val)


def bind(ma: Maybe[a], k: KleisliT) -> Maybe[b]:
    if type(ma) is Nothing:
        return Nothing()
    else:
        try:
            val = ma.val
            return k(val)
        except Exception:
            return Nothing()


Kleisli = kleisli_factory(bind)


def bind_chain(ma: Maybe[a], *ks: KleisliT) -> Maybe[b]:
    ret = ma
    for k in ks:
        ret = bind(ret, k)
    return ret


if __name__ == '__main__':

    assert bind(Just(3), Kleisli(lambda x: Just(x + 5))) == Just(8)
    assert bind(
                bind(Just(3),
                     Kleisli(lambda x: Just(x + 5))),
                Kleisli(lambda x: Just(x * 3))) == Just(24)
    
    assert bind_chain(Just(7),
                      Kleisli(lambda x: Just(x + 10)),
                      Kleisli(lambda x: Just(x * 3)),
                      Kleisli(lambda x: Just(x - 11))) == Just(40)

    assert bind_chain(Just(1),
                      Kleisli(lambda x: Just(x / 0)),
                      Kleisli(lambda x: Just(x + 3))) == Nothing()

    assert (Just(12)
            * Kleisli(lambda x: Just(x + 10)
                                * Kleisli(lambda x: Just(x * 3)))) == Just(66)

    assert (Just(30) *
            (Kleisli(lambda x: Just(x / 10)) * Kleisli(lambda x: Just(x + 3)))) == Just(6.0)
