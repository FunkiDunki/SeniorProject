import dataclasses as dc
from typing import List,  Tuple


@dc.dataclass
class Employee:
    """
    Employees are basic unit of scaling.
    Each employee has name, and stats, 
    as well as a list of their skill tags.
    """

    name: str
    salary: int  # how much does this employee earn in one year
    morale: float  # used to change efficiency
    tags: List[Tuple[str,int]]  #the list of skill tags where each one has an efficiency modifier between 0 and 100
