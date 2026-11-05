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

    def _get_center(self) -> tuple[float, float]:
        """
        Finding center of the symbol
        :return: returns the coordinates [x, y] of the symbol's center
        """
        cx = (self.xmin + self.xmax) / 2.0
        cy = (self.ymin + self.ymax) / 2.0

        return cx, cy