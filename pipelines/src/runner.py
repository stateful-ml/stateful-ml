from typing import Callable, Iterator


def run_etl[ET, TL](
    extract: Callable[[], Iterator[ET]],
    transform: Callable[[ET], TL],
    load: Callable[[TL], None],
):
    '''
    the default runner is just a simple synchronous batched runner
    '''
    for batch in extract():
        load(transform(batch))
