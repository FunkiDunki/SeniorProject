import dataclasses as dc

import numpy as np
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
