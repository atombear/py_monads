def unit(val):
    return lambda f: f(val)

def init(val):
    return unit(val)


def add(val):
    return lambda v: unit(v + val)


end = lambda x: x


if __name__ == '__main__':
    assert init(3)(add(7))(end) == 10
    assert init(20)(add(11))(add(35))(end) == 66
