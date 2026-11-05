from dataclasses import dataclass, field
from typing import List, Dict
from crochet_symbol import CrochetSymbol

@dataclass
class PatternAnalysisResult:
    # where start reading pattern
    beginning_side: str
    
    # list of symbols in each row
    rows: Dict[int, List[CrochetSymbol]] = field(default_factory=dict)

    @property
    def total_rows(self) -> int:
        """
        Amount of rows found in the diagram
        """
        return len(self.rows)