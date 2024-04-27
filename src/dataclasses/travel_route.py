import dataclasses as dc
import random
from typing import List, Tuple

import exceptions as ex
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


def random_travel_routes(locations: List[lc.Location]) -> List[TravelRoute]:
    """
    Generates a random number of unique travel routes from the current location
    to all locations to its right in the input list.
    """

    if len(locations) < 2:
        raise ex.CustomError("locations should have length of 2 or more")

    travel_routes: List[TravelRoute] = []

    for curr in range(len(locations) - 1):

        origin = locations[curr]
        possible_destinations = locations[curr + 1:].copy()
        num_desired = random.randint(1, len(possible_destinations))
        num_paths = 0

        while num_desired > num_paths:
            destination = random.choice(possible_destinations)
            travel_routes.append(random_travel_route(origin, destination))
            possible_destinations.remove(destination)
            num_paths += 1

    return travel_routes
