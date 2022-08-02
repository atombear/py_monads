class Maybe:
    def __init__(self, val, is_nothing=False):
        self.is_nothing = is_nothing
        self.val = val

    def __add__(self, other):
        if self.is_nothing:
            return self
        else:
            try:
                self.val += other
            except:
                self.is_nothing = True
            return self

    def __truediv__(self, other):
        if self.is_nothing:
            return self
        else:
            try:
                self.val /= other
            except:
                self.is_nothing = True
            return self

    def __eq__(self, other):
        if self.is_nothing:
            return self.is_nothing is other.is_nothing
        else:
            return (self.is_nothing is other.is_nothing
                    and self.val == other.val)


if __name__ == '__main__':
    v0 = Maybe(3)
    assert v0 + 3 + 10 == Maybe(16)

    v1 = Maybe(10)
    assert ((v1 + 10) / 0) + 8 == Maybe(0, True)
