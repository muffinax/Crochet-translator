from dataclasses import dataclass
from typing import Optional

@dataclass
class CrochetSymbol:
    type: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    confidence: float

    # Number of x-crochet symbol
    modifier: Optional[int] = None