import dataclasses as dc
import numpy as np

@dc.dataclass
class Item:
    '''
    Items need some sort of meaning, and some sort of name.
        For now, the meaning could be stored as a np array,
        and we can use np math functions for easy computations
    '''
    id: int
    name: str
    meaning: np.array

def item_similarity (i1: Item, i2: Item):
    '''
    INPUT: i1 and i2 are items
    RETURNS: cosine similarity (between -1, 1) of the meanings of the two items
    SIDE-EFFECTS: none
    '''
    dot = np.dot(i1.meaning, i2.meaning)
    norms = np.linalg.norm(i1.meaning) * np.linalg.norm(i2.meaning)
    return dot / norms #cosine similarity

def main():
    #example usage of Item dataclass
    my_item = Item(3, "wispsit", np.array([0.1, 0.5, 0.3, 0.9]))
    item2 = Item(15, "Spikechair", np.array([0.3, 0.1, 0.5, 0.6]))
    print(my_item)
    print(item2)
    #get similarity between the two items
    print(item_similarity(my_item, item2))

if  __name__ == "__main__":
    main()