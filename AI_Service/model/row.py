import itertools
from dataclasses import dataclass, field
from typing import List
from .crochet_symbol import CrochetSymbol

id_generator = itertools.count(0)

def reset_row_ids():
    global id_generator
    id_generator = itertools.count(0)

@dataclass
class Row:
    symbols: List[CrochetSymbol]
    is_reading_from_left: bool

    row_id: int = field(init=False)

    def __post_init__(self):
        self.row_id = next(id_generator)