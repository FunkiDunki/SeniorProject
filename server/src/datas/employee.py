import dataclasses as dc
import random
from typing import List, Tuple

from faker import Faker


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
    """
    tags is the list of skill tags where each one has an
    efficiency modifier between 0 and 100
    """
    tags: List[Tuple[str, int]]


def rand_employee() -> Employee:
    faker = Faker()

    name = faker.name()
    salary = random.randint(1, 1000)
    morale = random.uniform(1.0, 100.0)
    tags = [
        ("cooking", random.randint(0, 101)),
        ("fighting", random.randint(0, 101)),
        ("charisma", random.randint(0, 101)),
        ("critical_thinking", random.randint(0, 101)),
    ]

    return Employee(name, salary, morale, tags)
