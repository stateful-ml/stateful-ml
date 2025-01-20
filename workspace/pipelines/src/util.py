from typing import TypeVar, Iterable

T = TypeVar("T")


def by_chunks(x: Iterable[T], n: int) -> Iterable[list[T]]:
    values = []
    for value in x:
        values.append(value)
        if len(values) >= n:
            yield values
            values = []
    yield values
