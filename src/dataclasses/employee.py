import dataclasses as dc

import numpy as np


@dc.dataclass
class Employee:
    """
    Employees are basic unit of scaling.
    Each employee has name, and stats
    """

    name: str
    salary: int  # how much does this employee earn in one year
    morale: float  # used to change efficiency
