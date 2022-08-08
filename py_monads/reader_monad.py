r"""
the reader monad captures a function cfg -> a the monad itself is typed in
terms of the types of the input and output - Reader cfg a the function is
introduced to the constructor as eg runReader the monadic 'part' is Reader
cfg, which is to say for m a  = Reader cfg a, m = Reader cfg functions will
actually return themselves a function that is designed to ACT ON the config
as a final step. binding such monads together will effectively push the config
through the computation. what is happening during eg bind? essentially, the
monad wraps a function from a cfg to a type a. The function it is being
bound to goes from a to a similar monad, which itself wraps a function from a
cfg to a. so, for m a >>= (a -> m b), a is implicitly cfg -> a. what must be
done, when the confg is provided at the end, is that it must be passed to the
function in m a, and the output must then be passed to the bind target g, which
must then also accept the config.
if m a contains fa :: cfg -> a, and m b contains fb :: cfg -> b, the bind must
effect the following composition: \cfg -> g $ fa cfg $ cfg. so the bind target
g expects a, which is achieved by passing the cfg to fa, the function in the
monad of the bind source. g will return fb, which then expects a cfg. the
above expresses that.

the unit is very simple - unit(x) = Reader(lambda cfg: x). This can be
determined and confirmed from the identity laws.

expressing bind clearly:
(>>=) :: m a -> (a -> m b) -> m b
(>>=) (m a) f = m (\cfg -> runReader $ f $ a cfg $ cfg)

where a convenience function (runReader (Reader a) = a) has been assumed.

m a >>= return - m (\cfg -> runReader $ return $ a cfg $ cfg)
               - m (\cfg -> (runReader $ Reader (\x -> a cfg)) cfg
               - m (\cfg -> (\x -> a cfg) cfg)
               - m (\cfg -> a cfg)
               - m a

return a >>= (\x -> fma x) - m (\x -> a) >>= (\x -> fma x)
                           - m (\cfg -> runReader $ (\x -> fma x) $ (\x -> a) cfg $ cfg)
                           - m (\cfg -> runReader $ (\x -> fma x) a $ cfg)
                           - m (\cfg -> runReader $ fma a $ cfg)
                           - m (runReader (fma a))
                           - fma a

where fma is so-called because it is a function that takes a and produces a monad m a.

There is also a convenience monad Reader(\cfg -> cfg) used when there is syntax to
support writing nested lambdas in an 'imperative' style
"""
from dataclasses import dataclass
from typing import Callable, Tuple, TypeVar, Dict

from py_monads.monad import Monad, a, b, KleisliT, kleisli_factory


class Cfg:
    pass


CfgT = TypeVar('CfgT', bound=Cfg)


class Reader(Monad[a]):
    def __init__(self, f: Callable[[CfgT], a]):
        # f should be a function that accepts a cfg and returns a.
        self.bind = bind
        self.runReader: Callable[[CfgT], a] = f


def unit(val: a) -> Reader[a]:
    return Reader(lambda x: val)


def bind(r: Reader[a], k: KleisliT) -> Reader[b]:
    return Reader(lambda cfg: k(r.runReader(cfg)).runReader(cfg))


Kleisli = kleisli_factory(bind)


def example0():
    @dataclass
    class Letters(Cfg):
        first_letter: str
        second_letter: str

    @Kleisli
    def add_first_letter(x):
        return Reader(lambda cfg: x + cfg.first_letter)

    @Kleisli
    def add_second_letter(x):
        return Reader(lambda cfg: x + cfg.second_letter)

    m = unit('') * add_first_letter * add_second_letter * add_first_letter

    cfg = Letters('a', 'b')
    assert m.runReader(cfg) == 'aba'


def example_yao():
    @dataclass
    class ModifyMessage(Cfg):
        skip_letters: Tuple[str, ...]
        censor_words: Dict[str, str]

    mT = Callable[[ModifyMessage], str]

    def toUpperStr(s: str) -> Reader[mT]:
        def runReader(cfg: ModifyMessage) -> str:
            all_filter = lambda char: all(char.upper() != c.upper() for c in cfg.skip_letters)
            return ''.join(filter(all_filter, s.upper()))
        return Reader(runReader)

    def censorWords(s: str):
        def runReader(cfg: ModifyMessage) -> str:
            return ' '.join(cfg.censor_words.get(i.lower().strip('!.,'), i) for i in s.split(' '))
        return Reader(runReader)

    def welcomeMessage(motd: str, uname: str) -> Reader[mT]:
        return (toUpperStr(motd) * (lambda motd_upper:
                toUpperStr(uname) * (lambda uname_upper:
                unit(f'Welcome, {uname_upper}! MOTD: {motd_upper}'))))
    sl = ModifyMessage(('e', 'l'), {'toast': 'bread', 'freedom': 'labor'})
    r = welcomeMessage("another terrible day.", "ahmed biryani")
    assert r.runReader(sl) == 'Welcome, AHMD BIRYANI! MOTD: ANOTHR TRRIB DAY.'

    def fullMessage(motd: str, uname: str, jovial_msg: str) -> Reader[mT]:
        r = welcomeMessage(motd, uname) * (lambda welcome_message:
            censorWords(jovial_msg) * (lambda censored_message:
                 unit(welcome_message + " " + censored_message)))
        return r

    assert (fullMessage("another terrible day.", "ahmed biryani", "Good luck today! Seek freedom! Toast your spirit!").runReader(sl)
            == 'Welcome, AHMD BIRYANI! MOTD: ANOTHR TRRIB DAY. Good luck today! Seek labor bread your spirit!')


if __name__ == '__main__':
    example0()
    example_yao()
