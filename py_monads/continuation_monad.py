from functools import reduce


def unit(val):
    return lambda f: f(val)


def bind(monad, kiesli):
    return monad(kiesli)


def associate(k0, k1):
    return lambda x: k0(x)(k1)


def run_monad(monad):
    return monad(lambda x: x)


######## another formulation ############
def init(val):
    return unit(val)


def add(val):
    return lambda v: unit(v + val)


end = lambda x: x


if __name__ == '__main__':
    assert init(3)(add(7))(end) == 10
    assert init(20)(add(11))(add(35))(end) == 66
    assert run_monad(init(3)(add(7))(add(4))) == 14

    m = unit(10)
    m = bind(m, lambda x: unit(x + 10))
    m = bind(m, lambda x: unit(x + 33))
    assert run_monad(m) == 53

    m = unit(12)
    k = associate(lambda x: unit(x+1), lambda x: unit(x+2))
    m = bind(m, k)
    assert run_monad(m) == 15

    m = unit(23)
    k = reduce(associate,
               (lambda x: unit(x+3),
                lambda x: unit(x*2),
                lambda x: unit(x-2),
                lambda x: unit(x/2)))
    m = bind(m, k)
    assert run_monad(m) == 25.0
