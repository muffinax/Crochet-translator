from __future__ import annotations
import itertools

from typing import List
from math import sqrt
from dataclasses import dataclass, field
from typing import Optional

id_generator = itertools.count(0)

def reset_symbol_ids():
    global id_generator
    id_generator = itertools.count(0)

@dataclass
class CrochetSymbol:
    type: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    confidence: float

    symbol_id: int = field(init=False)

    height: int = field(init=False)
    width: int = field(init=False)
    cx: float = field(init=False)
    cy: float = field(init=False)
    ratio: float = field(init=False)

    connected_with: List[int] = field(init=False)
    is_base: bool = field(init=False)
    is_connectable: bool = field(init=False)

    def __post_init__(self):
        self.symbol_id = next(id_generator)

        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin

        """
        Aspect Ratio:
         < 1.0 -> horizontal oval
         == 1.0 -> circle
         > 1.0 -> vertical oval
        """
        self.ratio = self.height / self.width if self.width > 0 else 0
        self.is_base = False
        self.is_connectable = True
        self.connected_with = []

        self.cx = (self.xmin + self.xmax) / 2.0
        self.cy = (self.ymin + self.ymax) / 2.0
        
    def x_distance(self, other: CrochetSymbol):
        if self.cx >= other.cx:
            return self.cx - other.cx
        else:
            return other.cx - self.cx

    def y_distance(self, other: CrochetSymbol):
        if self.cy >= other.cy:
            return self.cy - other.cy
        else:
            return other.cy - self.cy

    def distance(self, other: CrochetSymbol):
        x = self.x_distance(other)
        y = self.y_distance(other)
        return sqrt(x*x + y*y)
