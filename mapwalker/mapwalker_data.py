from dataclasses import dataclass
from typing import List, Tuple
from pydantic import BaseModel

@dataclass
class Node:
    node_id: str
    node_description: str

@dataclass
class Edge:
    from_id: str
    to_id: str

@dataclass
class World:
    nodes: List[Node]
    edges: List[Edge]

@dataclass
class Player:
    location: str

class GenerateReturn(BaseModel):
    node_description: str
    outgoing_connections: list[str]