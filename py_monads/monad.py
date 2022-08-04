from typing import Generic, TypeVar, Callable

a, b = map(TypeVar, 'ab')

KliesliT = TypeVar('KliesliT')


class Monad(Generic[a]):
    bind: None

    def __mul__(self, other):
        return self.bind(self, other)


def kliesli_factory(bind: Callable[[Monad[a], KliesliT], Monad[b]]):
    class Kliesli:
        def __init__(self, f: Callable[[a], Monad[b]]):
            self.f = f

        def __call__(self, val: a) -> Monad[b]:
            return self.f(val)

        def __mul__(self, other: KliesliT) -> KliesliT:
            """Associativity of monadic composition, eg m >>= (f >>= g)"""
            return Kliesli(lambda x: bind(self.f(x), other))

    return Kliesli
