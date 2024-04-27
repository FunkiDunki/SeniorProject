import dataclasses as dc
import population as pl


@dc.dataclass
class SalesLedger:
    item: int
    population: pl.Population
    price: float
    volume: int
