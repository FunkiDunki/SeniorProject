import dataclasses as dc

import population as pl


@dc.dataclass
class SalesLedger:
    """
    A sales ledger is a storage method for historical sales.
    """

    item: int
    population: pl.Population
    price: float
    volume: int
