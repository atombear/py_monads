r"""
the writer monad is the counterpart to the reader monad - rather than threading
an input value through a program, the writer monad performs the much simpler
task of amending to the output an item that is then carried through the program.
this is a simpler task, resulting in a simpler implementation, because the
change is only to the output in a very predictable and minor fashion.

the implementation will largely mirror Reader.

there are some other useful functions -

listen injects the log into the output for downstream perusal.
listen :: Writer Log a -> Writer Log (a, Log)

tell is almost like unit for a log
tell :: Log -> Writer Log ()

Log should belong to the class of monoids, for which two important
functions are defined. generally, a monoid comprises a set of elements
closed under a binary operation, where one element is neutral wrt the
binary operation.

mappend :: Monoid a => a -> a -> a
mempty  :: Monoid a => a
"""
from typing import TypeVar, Tuple

from py_monads.monad import Monad, a, b, KleisliT, kleisli_factory, lapp


class Log:
    pass


class EmptyLog(Log):
    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other


LogT = TypeVar('LogT', bound=Log)


class Writer(Monad[a]):
    def __init__(self, runWriter: Tuple[LogT, a]):
        self.bind = bind
        self.runWriter = runWriter


def unit(val: a) -> Writer[a]:
    return Writer((EmptyLog(), val))


def bind(wa: Writer[a], k: KleisliT) -> Writer[b]:
    loga, vala = wa.runWriter
    logb, valb = k(vala).runWriter
    return Writer((loga + logb, valb))


Kleisli = kleisli_factory(bind)


def log(s: a) -> Writer[None]:
    return Writer((s, None))


def example_yao():
    def addTwo(val: int) -> Writer[int]:
        return log('adding 2\n') * (lambda _:
               unit(val + 2))

    def augmentAndStringify(x: int, y: int) -> Writer[int]:
        return log('augmenting...\n') * (lambda _:
               addTwo(x) * (lambda xp:
               addTwo(y) * (lambda yp:
               lapp(5 * xp)(lambda xpp:
               log('stringify...\n') * (lambda _:
               unit(str(xpp + yp)))))))

    final_log, final_value = augmentAndStringify(10, 11).runWriter
    assert final_log == 'augmenting...\nadding 2\nadding 2\nstringify...\n'
    assert final_value == '73'


if __name__ == '__main__':
    example_yao()
