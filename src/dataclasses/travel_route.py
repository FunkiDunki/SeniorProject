import dataclasses as dc
import location
from typing import Tuple


@dc.dataclass
class TravelRoute:
    """
    A travel route is an edge of a world graph in which
    a location is a vertex. It has two locations, the
    distance between them, and the type of travel used
    to get from one to the other.
    """

    locations: Tuple[location.Location, location.Location]
    distance: float
    travel_type: str
