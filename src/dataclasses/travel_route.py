import dataclasses as dc
from typing import Tuple
import random
import location as lc


@dc.dataclass
class TravelRoute:
    """
    A travel route is an edge of a world graph in which
    a location is a vertex. It has two locations, the
    distance between them, and the type of travel used
    to get from one to the other.
    """

    locations: Tuple[lc.Location, lc.Location]
    distance: int
    travel_type: str


def random_travel_route(start: lc.Location, end: lc.Location) -> TravelRoute:
    """
    generates a random travel route between two given locations
    """

    locations = (start, end)
    distance = random.randint(1, 100)
    travel_type = random.choice(["land", "water", "air"])

    return TravelRoute(locations, distance, travel_type)
