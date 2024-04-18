import dataclasses as dc
import graph


@dc.dataclass
class World:
    """
    World has a map that is a graph which should contain
    a list of locations as the vertices and a list of
    travel routes as edges.
    """

    map: graph.Graph
