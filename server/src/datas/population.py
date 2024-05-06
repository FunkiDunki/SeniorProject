import dataclasses as dc

from . import exceptions as ex
from . import item as im
import numpy as np
from numpy import ndarray


@dc.dataclass
class Population:
    """
    Populations have size, and a representation of current state.
    Ideally, the needs match the meanings of items.
    """

    size: int  # size is count of population
    needs_state: ndarray


def default_needs(len: int):
    """
    Creates and returns a valid needs_state
    INPUT: how many need factors exist
    RETURN: a valid needs_state
    """

    return np.random.rand(len)


def initialize_population(size: int) -> Population:
    """
    initialize a population with a certain size.
    INPUT: size
    OUTPUT: population with given size, and default needs
    """

    pop = Population(size, default_needs(3))
    return pop


def update_needs(pop: Population, item_purchased: im.Item) -> ndarray:
    """
    INPUT: a population pop, and an item purchased by pop
    OUTPUT: ndarray representing updated needs_state of pop
    SIDE EFFECTS: none
    """

    if len(pop.needs_state) != len(item_purchased.meaning):
        ex.CustomError("needs state and item meaning must be same length")

    return np.add(pop.needs_state, item_purchased.meaning)
