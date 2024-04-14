import dataclasses as dc
import graph

@dc.dataclass
class World:
    map: graph.Graph
