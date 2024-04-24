import dataclasses as dc
from typing import List
import location as lc
import travel_route as tr
import random


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

    locations = [lc.random_location() for _ in range(random.randint(1, 100))]
    travel_routes = tr.random_travel_routes(locations)

    return World(locations, travel_routes)
