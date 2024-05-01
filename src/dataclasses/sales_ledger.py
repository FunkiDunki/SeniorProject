import dataclasses as dc
from typing import List

import numpy as np
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


def calculate_item_price(
    population: pl.Population, sale_history: List[SalesLedger]
) -> float:
    """
    INPUT: population is the population you are selling to
    and sales_history is a list of sales ledgers which
    document sales of this item to this population
    RETURNS: a price for the item
    ERROR: none
    SIDE-EFFECTS: none
    This function calculates the price an item should be sold at.
    This is a barebones placeholder implementation.
    """

    num_sales = len(sale_history)

    if num_sales == 0:
        return 100

    avg_selling_price = sum(sale.price for sale in sale_history) / num_sales
    demand: float = float(np.linalg.norm(population.needs_state))

    return avg_selling_price * demand
