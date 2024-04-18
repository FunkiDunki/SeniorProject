import dataclasses as dc

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
