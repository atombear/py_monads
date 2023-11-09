import copy
from typing import TypeVar, Generic, Callable, Any, Type

S = TypeVar("S")  # Struct
A = TypeVar("A")  # Attr

View = Callable[[S], Any]
Set = Callable[[Any, S], S]


class ModifyStruct:
    def modify(self, **kwargs) -> "ModifyStruct":
        d: dict = copy.deepcopy(self.__dict__)
        d.update(kwargs)
        return type(self)(**d)

    def __repr__(self) -> str:
        return str(self.__dict__)


class Lens(Generic[S, A]):
    def __init__(self, attr: str, view, set):
        self.attr: A = attr
        self.view: View = view
        self.set: Set = set

    def __call__(self, other: "Lens") -> "Lens":
        return Lens(
            attr=f"{self.attr}.{other.attr}",
            view=lambda struct: other.view(self.view(struct)),
            set=lambda value, struct: self.set(
                other.set(value, self.view(struct)), struct
            ),
        )


def lens_ms(attr: str) -> Lens:
    return Lens(
        attr=attr,
        view=lambda struct: getattr(struct, attr),
        set=lambda value, struct: struct.modify(**{attr: value}),
    )


def lens_tup(idx: str) -> Lens:
    return Lens(
        attr=idx,
        view=lambda tup: tup[idx],
        set=lambda value, tup: tuple(
            value if jdx == idx else tup[jdx] for jdx, val in enumerate(tup)
        ),
    )


def lens_dict(key: str) -> Lens:
    return Lens(
        attr=key,
        view=lambda d: d[key],
        set=lambda value, d: {k: (value if k == key else d[k]) for k in d},
    )


if __name__ == "__main__":

    class A(ModifyStruct):
        def __init__(self, d):
            self.d = d

    ld = lens_ms("d")
    l_hello = lens_dict("hello")
    l0 = lens_tup(0)

    o = A(d={"hello": (10, 11, 12)})

    print(ld(l_hello)(l0).set(20, o))
