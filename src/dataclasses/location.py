import dataclasses as dc
import population as p
from typing import List


@dc.dataclass
class Location:
    """
    A Location is a node that represents a location on a world map. 
    It has a name, a list of resources obtainable at this location,
    and a native people which is represented by a population object.
    """

    name: str
    resources: List[any]
    native_people: p.Population
