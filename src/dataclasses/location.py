import dataclasses as dc

@dc.dataclass
class Location:
    name: str
    resources: dict
    native_people: dict

