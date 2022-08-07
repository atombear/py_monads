r"""
the state monad is reminiscent of the reader monad but with the added functionality that the state can be modified.

the type State s a corresponds to a function \s -> (s, a). bind will accept the following inputs:

ma    :: State s a
ka_mb :: a -> State s b

each monad carries a function fa :: s -> (s, a).

composition, then, must produce the monad mb, carrying a function fb :: s -> (s, b), that implicitly must be carrying
information regarding the state of ma. working backwards, the function fb will accept state s, which it must first
thread to fa. fa will produce a which it will push to ka_mb, whose return will ultimately be the return of the
composition.

\s -> runState (ka_mb $ snd $ (fa s)) $ (fst $ (fa s))

where runState is a convenience function that produces fa from ma.

this is complicated, so, step by step. the composition must produce a State which is constructed on a function
s -> (s, b). we construct this function piece by piece. the state that is given to this function must 'obviously' first
pass through fa, which is the function owned by the first monadic argument to bind. this will produce (s', a). a
must 'obviously' be passed to the kleisli arrow, producing a monad mb. even though it is the correct type, if we return
mb now, we will be discarding the state output by fa s. if we unpack from mb its function fb, and pass s' to  it, we
will have (s'', b), which is correct. in total, we have a function that accepts s and produces (s'', b), which is
exactly the type signature we expect. s'' is obtained by passing s into fa which yields (s', a), then passing s' into
fb. fb is obtained by passing the aforementioned a into ka_mb.
"""
from typing import Callable, Tuple, TypeVar, Generic

from py_monads.monad import Monad, a, b, KleisliT, kleisli_factory


class St:
    pass


StT = TypeVar('StT', bound=St)


class State(Monad[a]):
    def __init__(self, f: Callable[[StT], Tuple[StT, a]]):
        self.bind = bind
        self.runState: Callable[[StT], Tuple[StT, a]] = f


def unit(val: a) -> State[a]:
    return State(lambda x: (x, val))


def bind(state: State[a], k: KleisliT) -> State[b]:
    def runState(s: StT) -> Tuple[StT, b]:
        (sp, vala) = state.runState(s)
        return k(vala).runState(sp)
    return State(runState)


Kleisli = kleisli_factory(bind)


def example0():
    class ListState(Generic[a], St, list):
        pass

    @Kleisli
    def advance_list(v: a) -> State[a]:
        return State(lambda s: (s + [v], v+1))

    def make_list(max_val: int) -> ListState[int]:
        m = unit(0) * (advance_list ** max_val)
        return m.runState(ListState())[0]

    assert make_list(5) == list(range(6))


if __name__ == '__main__':
    example0()
