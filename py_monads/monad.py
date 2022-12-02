from functools import reduce
from typing import Generic, TypeVar, Callable

a, b, r = map(TypeVar, 'abr')


class Monad(Generic[a]):
    bind = None

    def __mul__(self, other):
        return self.bind(self, other)


Monad_a_T = TypeVar('Monad_a_T', bound=Monad[a])
Monad_b_T = TypeVar('Monad_b_T', bound=Monad[b])


class KleisliBase:
    def __init__(self, f: Callable[[a], Monad_b_T]):
        self.f = f

    def __call__(self, val: a) -> Monad_b_T:
        return self.f(val)


KleisliT = TypeVar('KleisliT', bound=KleisliBase)


def kleisli_factory(bind: Callable[[Monad_a_T, KleisliT], Monad_b_T]):
    class Kleisli(KleisliBase):
        def __mul__(self, other: KleisliT) -> KleisliT:
            """Associativity of monadic composition, eg m >>= (f >>= g)"""
            return Kleisli(lambda x: bind(self.f(x), other))

        def __pow__(self, n: int) -> KleisliT:
            return reduce(lambda x, y: x * y, (self for _ in range(n)), self)

    return Kleisli


def lapp(val):
    return lambda f: f(val)
