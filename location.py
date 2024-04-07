import dataclasses as dc

@dc.dataclass
class Location:
    name: str
    resources: dict
    native_people: dict
    land_neighbors: dict
    water_neighbors: dict
    sky_neighbors: dict