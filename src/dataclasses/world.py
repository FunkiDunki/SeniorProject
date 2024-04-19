import dataclasses as dc
from typing import List
import location as lc
import travel_route as tr


@dc.dataclass
class World:
    """
    World has a map that is a graph which should contain
    a list of locations as the vertices and a list of
    travel routes as edges.
    """

    locations: List[lc.Location]
    travel_routes: List[tr.TravelRoute]
