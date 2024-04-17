import dataclasses as dc
from typing import List, Tuple


@dc.dataclass
class Recipe:
    """
    A recipe has a list of it's ingredients and how many of each ingredient is necessary, as well as
    how long the recipe would take to produce based on the qualifications of the employee. Also the
    ID of the output item as well as how many of that item will be created from this recipe.
    """

    ingredients: List[
       Tuple[int, int]
    ]  # a list of tuples where the first part is an item id and the second is the amount of that item
    timeRequired: List[
       Tuple[str, int]
    ]  # the tuples are an employee skill tag, and how long it would take that tag to complete the recipe
    outputID: int  # the id for the new item produced by the recipe
    outputAmt: int  # the amount of new items this recipe produces