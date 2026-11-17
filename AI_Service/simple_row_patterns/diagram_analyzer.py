from model.crochet_symbol import CrochetSymbol
from model.row import Row, reset_row_ids
from typing import List, Dict, Any
from simple_row_patterns.symbol_anayzer import SymbolAnalyzer

import numpy as np

class DiagramAnalyzer:
    def __init__(self, image: np.array, tolerance: float = 0.5):
        """
        Class analyzing rows, pattern boundaries, and starting points.
        :param tolerance: symbol center boundaries multiplier
        """
        self.tolerance = tolerance
        self.symbol_analyzer = SymbolAnalyzer(image)

    def _find_first_row(self, symbols: List[CrochetSymbol]) -> List[CrochetSymbol]:
        """
        Finding the first (base) row.
        :param symbols: list of detected symbols
        :return: list of symbols in the first row
        """
        base_chains = [s for s in symbols if s.ratio < 1 and s.type == "chain" ] 
        
        if not base_chains:
            return [] # There are no chains
            
        # Looking for the lowest chain
        lowest_chain = max(base_chains, key=lambda s: s.cy)
        lowest_y = lowest_chain.cy
        
        # Counting average height
        avg_height = sum(s.height for s in base_chains) / len(base_chains)
        tolerance = avg_height #* self.tolerance
        
        # Looking for chains in the same row within the tolerance
        first_row_symbols = [
            s for s in base_chains 
            if abs(s.cy - lowest_y) <= tolerance
        ]

        for s in first_row_symbols:
            s.is_base = True
        
        # Sorting chains from left to right
        first_row_symbols.sort(key=lambda s: s.cx)
    
        return first_row_symbols 

    def prepare_base_symbols(self, symbols: List[CrochetSymbol]) -> List[Row]:
        """
        Prepare first row and chain transactions
        """

        base_row = self._find_first_row(symbols)

        if not base_row:
            return []

        # start of the "cnter of the diagram"
        xmin = min(s.xmax for s in base_row)
        xmax = max(s.xmin for s in base_row)

        edge_chains = [s for s in symbols if s.ratio > 1.1 and s.type == "chain" and (s.cx < xmin or s.cx > xmax)]
        edge_groups = []

        if edge_chains:
            edge_chains.sort(key=lambda s: s.cy, reverse=True)
            current_group = []

            for chain in edge_chains:
                chain.is_base = True
                chain.is_connectable = False
                if not current_group:
                    current_group.append(chain)
                else:
                    last_chain = current_group[-1]
                    if chain.x_distance(last_chain) <= chain.width * 1.5:
                        current_group.append(chain)
                    else:
                        current_group[-1].is_connectable = True
                        edge_groups.append(current_group)
                        current_group = [chain]

            if current_group:
                current_group[-1].is_connectable = True
                edge_groups.append(current_group)

        return base_row, edge_groups

    def locate_symbols(self, symbols: List[CrochetSymbol]) -> List[CrochetSymbol]:
        if not symbols:
            return []
        
        for symbol in symbols:
            if symbol.is_base == True:
                continue

            if symbol.type == "slip-stitch" or symbol.type == "slip-stich":   #later delete slip-stich - error in nameing first class
                symbol.connected_with = self.symbol_analyzer.place_stitch(symbol, symbols)
            elif symbol.type == "single-crochet":
                symbol.connected_with = self.symbol_analyzer.place_scrochet(symbol, symbols)
            elif symbol.type == "chain":
                symbol.connected_with = self.symbol_analyzer.place_chain(symbol, symbols)
            else:
                symbol.connected_with = self.symbol_analyzer.place_crochet(symbol, symbols)

        return symbols