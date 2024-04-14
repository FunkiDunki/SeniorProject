import dataclasses as dc

@dc.dataclass
class TravelRoute:
    distance: float
    travel_type: str
    locations: tuple