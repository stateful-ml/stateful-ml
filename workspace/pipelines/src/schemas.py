from dataclasses import dataclass
from numpy.typing import NDArray
import polars as pl


@dataclass(frozen=True)
class Dataset:
    data: NDArray
    metadata: pl.DataFrame
