import dataclasses as dc
import random
from typing import List

from . import location as lc
from . import travel_route as tr


@dc.dataclass
class World:
    """
    World has a map that is a graph which should contain
    a list of locations as the vertices and a list of
    travel routes as edges.
    """

    locations: List[lc.Location]
    travel_routes: List[tr.TravelRoute]


def random_world() -> World:
    """
    generates a random world
    """

    locations = [lc.random_location() for _ in range(random.randint(2, 100))]
    travel_routes = tr.random_travel_routes(locations)

    return World(locations, travel_routes)
