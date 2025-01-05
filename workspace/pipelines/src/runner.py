from typing import Callable, Iterator, TypeVar

ET = TypeVar("ET")
TL = TypeVar("TL")


def run_etl(
    extract: Callable[[], Iterator[ET]],
    transform: Callable[[ET], TL],
    load: Callable[[TL], None],
):
    """
    the default runner is just a simple synchronous batched runner
    """
    for batch in extract():
        load(transform(batch))
