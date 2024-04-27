import dataclasses as dc
import numpy as np
import population as pl
import sales_ledger as sl
from typing import List
from numpy import ndarray


@dc.dataclass
class Item:
    """
    Items need some sort of meaning, and some sort of name.
    For now, the meaning could be stored as a np array,
    and we can use np math functions for easy computations
    """

    id: int
    name: str
    meaning: ndarray


def item_similarity(i1: Item, i2: Item):
    """
    INPUT: i1 and i2 are items
    RETURNS: cosine similarity (between -1, 1) of the meanings of the two items
    ERROR: value_error if not same size
    SIDE-EFFECTS: none
    """
    if np.size(i1.meaning) != np.size(i2.meaning):
        raise ValueError("mismatch size")
    dot = np.dot(i1.meaning, i2.meaning)
    norms = np.linalg.norm(i1.meaning) * np.linalg.norm(i2.meaning)
    return dot / norms  # cosine similarity


def calculate_item_price(population: pl.Population,
                         sale_history: List[sl.SalesLedger]) -> float:
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

    if len(sale_history) == 0:
        return 100

    avg_selling_price = (
        sum(sale.price for sale in sale_history)/len(sale_history)
    )
    demand: float = float(np.linalg.norm(population.needs_state))

    return avg_selling_price * demand
