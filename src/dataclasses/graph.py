import dataclasses as dc
from typing import List


@dc.dataclass
class Graph:
    """
    Graph has a list of vertices V and a list of edges E.
    """

    V: List[any]
    E: List[any]
