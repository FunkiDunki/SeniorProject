import dataclasses as dc
import location as l
from typing import Tuple

@dc.dataclass
class TravelRoute:
    """
    A travel route is an edge of a world graph in which 
    a location is a vertex. It has two locations, the 
    distance between them, and the type of travel used
    to get from one to the other.
    """

    locations: Tuple[l.Location, l.Location]
    distance: float
    travel_type: str
    