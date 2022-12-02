r"""
bind should take a continuation (a-r)->r, and a kleisli a->(b->r)->r, and return a continuation (b->r)->r. we can count
types to understand how this should work. the most important 'action' is switching the order of inputs.

the resulting continuation expects a function (b->r), which the kleisli accepts as its second argument, resulting in a
function (a->r) which the original continuation consumes.

thus

bind c k = \br -> (c (\a -> (k a br)))

with parentheses for emphasis. to wit: the kleisli is formed into a function (\a -> k a br), which has type (a->r),
this function is then passed to the original continuation.

how do we combine kleisli arrows? first, what arrows are allowed to combine and what is the resulting type? consider the
transformation

((a->r)->r) -> (a->(b->r)->r) -> ((b->r)->r) -> (b->(c->r)->r) -> ((c->r)->r)

we can remove the intermediate continuation

((a->r)->r) -> (a->(b->r)->r) -> (b->(c->r)->r) -> ((c->r)->r)

and this is equivalent to

((a->r)->r) -> (a->(c->r)->r) -> ((c->r)->r)

therefore

(a->(b->r)->r) -> (b->(c->r)->r) -> (a->(c->r)->r)

similarly, by swapping inputs we can reason about the functional composition required here. the resulting kleisli
accepts two arguments, a, and (c->r)

kcomp k0 k1 = \a -> \cr -> ( (\br -> k0 a br) (\b -> k1 b cr) )

so a is used to form a function (\br -> k0 a br) of type ((b->r)->r), and the input of type (c->r) is used to form a
function (\b -> k1 b cr) of type (b->r), which is passed into the first function, to return r.

elementary.
"""
from typing import Callable

from py_monads.monad import Monad, a, r, KleisliT


def unit(x):
    return lambda f: f(x)


def bind(c, k):
    return lambda br: c(lambda a: k(a)(br))


def kleisli_composition(k0, k1):
    return lambda a: lambda cr: (lambda br: k0(a)(br))(lambda b: k1(b)(cr))


class Continuation(Monad[a]):
    def __init__(self, con: Callable[[Callable[[a], r]], r]):
        self.cont = con

    def bind(self, k: KleisliT) -> Monad[a]:
        return Continuation(bind(self.cont, k))

    def run_cont(self):
        return self.cont(lambda x: x)


if __name__ == '__main__':
    c = Continuation(unit(3)).bind(lambda x: unit(x*10)).bind(lambda x: unit(str(x))).bind(lambda x: unit(x + " children")).bind(lambda x: unit(len(x)))
    print(c.run_cont())

    eye = lambda x: x

    print(
        bind(
            bind(unit(10),
                 lambda x: unit(x+2)),
            lambda x: unit(10*x))
        (eye)
    )

    print(
        bind(unit(10),
            kleisli_composition(
                lambda x: unit(x+2),
                lambda x: unit(10*x)))
        (eye)
    )
