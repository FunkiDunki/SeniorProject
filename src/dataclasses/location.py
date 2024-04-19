import dataclasses as dc
from typing import List
from faker import Faker
import population as pl


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
