import dataclasses as dc
import json
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

    name: str
    locations: List[lc.Location]
    travel_routes: List[tr.TravelRoute]


def random_world(name: str) -> World:
    """
    generates a random world
    """

    locations = [lc.random_location() for _ in range(random.randint(2, 100))]
    travel_routes = tr.random_travel_routes(locations)

    return World(name, locations, travel_routes)


def test_world(name: str) -> World:
    """
    Test world that is small and simple to test endpoints
    """

    l1 = lc.test_location()
    l2 = lc.test_location()
    locations = [l1, l2]

    travel_routes = [tr.random_travel_route(l1, l2)]

    return World(name, locations, travel_routes)


def world_to_JSON(world: World) -> str:

    world_graph = {
        "name": world.name,
        "locations": [location.name for location in world.locations],
        "travel_routes": [
            [route.origin.name, route.destination.name]
            for route in world.travel_routes
        ],
    }

    return json.dumps(world_graph)
