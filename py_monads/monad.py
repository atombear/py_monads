from typing import Generic, TypeVar, Callable

a, b = map(TypeVar, 'ab')

KleisliT = TypeVar('KleisliT')


class Monad(Generic[a]):
    bind = None

    def __mul__(self, other):
        return self.bind(self, other)


def kleisli_factory(bind: Callable[[Monad[a], KleisliT], Monad[b]]):
    class Kleisli:
        def __init__(self, f: Callable[[a], Monad[b]]):
            self.f = f

        def __call__(self, val: a) -> Monad[b]:
            return self.f(val)

        def __mul__(self, other: KleisliT) -> KleisliT:
            """Associativity of monadic composition, eg m >>= (f >>= g)"""
            return Kleisli(lambda x: bind(self.f(x), other))

    return Kleisli
