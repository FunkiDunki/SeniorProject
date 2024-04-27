import dataclasses as dc
import random
from typing import List

import population as pl
from faker import Faker


@dc.dataclass
class Location:
    """
    A Location is a node that represents a location on a world map.
    It has a name, a list of resources obtainable at this location,
    and a native people which is represented by a population object.
    """

    name: str
    resources: List[int]
    native_people: pl.Population


def random_name() -> str:
    """
    generates a fake city name for a location
    """

    fake = Faker()
    return fake.city()


def random_location() -> Location:
    """
    generates a random location
    """

    name = random_name()
    resources = [random.randint(1, 100) for _ in range(random.randint(1, 100))]
    native_people = pl.initialize_population(random.randint(1, 100))

    return Location(name, resources, native_people)
