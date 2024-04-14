import dataclasses as dc
from typing import List

@dc.dataclass
class Graph:
    V: List[any]
    E: List[any]