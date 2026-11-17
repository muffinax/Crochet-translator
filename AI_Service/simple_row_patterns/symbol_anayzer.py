import numpy as np
from model.crochet_symbol import CrochetSymbol
from image_processor import ImageProcessor
from typing import List, Dict, Any

class SymbolAnalyzer:
    def __init__(self, full_image: np.ndarray):
        self.processor = ImageProcessor()
        self.full_image = full_image

    def lowest_point(self, symbol: CrochetSymbol):
        if symbol.type == "chain" or symbol.type == "slip-stitch" or symbol.type == "slip-stich":
            return None

        frame_y = -0.1
        frame_x = -0.1
        
        result = self.processor.prepare_symbol(self.full_image, symbol, frame_y, frame_x)
        
        if result[0] is None:
            return None
            
        clean_binary, roi_xmin, roi_ymin = result
        y_coords, x_coords = np.nonzero(clean_binary)
        
        # If the image is completely empty, return None
        if len(y_coords) == 0:
            return (symbol.cx, symbol.ymax)
            
        # The visually "lowest" point on the screen
        bottom_y = np.max(y_coords)
        
        # Extracting all X coordinates that belong to this bottom-most Y row
        x_at_bottom = x_coords[y_coords == bottom_y]

        line_xmin = np.min(x_at_bottom)
        line_xmax = np.max(x_at_bottom)
        
        # Finding middle X pixel
        mid_x = int((line_xmin + line_xmax) / 2)

        global_x = mid_x + roi_xmin
        global_y = bottom_y + roi_ymin
        
        return (global_x, global_y)

    def place_stitch(self, symbol, symbols: List[CrochetSymbol]):
        if symbol.type != "slip-stitch" and symbol.type != "slip-stich":   #later delete slip-stich - error in nameing first class
            return []

        return self._find_parent(
            symbol=symbol, 
            symbols=symbols, 
            target_x=symbol.cx, 
            target_y=symbol.ymax,
            search_width=symbol.width * 0.75, 
            search_depth=symbol.height * 2.0
        )

    def place_scrochet(self, symbol, symbols: List[CrochetSymbol]):
        if symbol.type != "single-crochet":
            return []

        return self._find_parent(
            symbol=symbol, 
            symbols=symbols, 
            target_x=symbol.cx, 
            target_y=symbol.ymax, 
            search_width=symbol.width * 0.6, 
            search_depth=symbol.height * 1.5
        )

    def place_crochet(self, symbol, symbols: List[CrochetSymbol]):
        if symbol.type in ("slip-stitch", "single-crochet", "chain", "slip-stich"):   #later delete slip-stich - error in nameing first class
            return []

        lowest_pt = self.lowest_point(symbol)
        if not lowest_pt:
            return []

        lowest_x, lowest_y = lowest_pt

        slant_distance = abs(lowest_x - symbol.cx)  #how far is the lowest point from center x

        if slant_distance < (symbol.width * 0.1):
            # loqwest point in the middle
            search_width = symbol.width * 0.5
        else:
            # width is too big because its not straight crochet
            search_width = symbol.width * 0.25
        
        return self._find_parent(
            symbol = symbol, 
            symbols = symbols, 
            target_x = lowest_x,
            target_y = lowest_y, 
            search_width = search_width,
            search_depth = symbol.height * 1.25
        )

    def place_chain(self, symbol, symbols: List[CrochetSymbol]):
        if symbol.type != "chain":
            return []

        # Checking if there arent any saved connections already
        if not getattr(symbol, 'connected_with', None):
            symbol.connected_with = []

        tolerance = int((symbol.height + symbol.width)/2)

        max_search_x = tolerance * 3.0
        
        left_candidates = []
        right_candidates = []
        
        # Contrlos if there are already saved symbols
        has_left = False
        has_right = False

        for conn_id in symbol.connected_with:
            conn_sym = next((x for x in symbols if x.symbol_id == conn_id), None)
            if conn_sym:
                if conn_sym.cx < symbol.cx:
                    has_left = True
                else:
                    has_right = True

        # if both are known then stop searching for them
        if has_left and has_right:
            return symbol.connected_with

        for s in symbols:
            if s.symbol_id == symbol.symbol_id or s.symbol_id in symbol.connected_with:
                continue
                
            if s.type not in ("slip-stitch", "single-crochet", "chain", "slip-stich"):
                y_match = (s.ymin - symbol.height <= symbol.cy <= s.ymin + s.height * 0.15)
            else:
                y_match = abs(s.cy - symbol.cy) <= symbol.height * 1

            if not y_match:
                continue

            # adding symbol to candidates list only if there isnt one saved
            if not has_left and s.cx < symbol.cx and (symbol.cx - s.xmax) < max_search_x and getattr(s, 'is_connectable', True):
                left_candidates.append(s)
            elif not has_right and s.cx > symbol.cx and (s.xmin - symbol.cx) < max_search_x and getattr(s, 'is_connectable', True):
                right_candidates.append(s)

        # LEFT SYMBOLS
        if left_candidates and not has_left:
            best_left = min(
                left_candidates,
                key=lambda s: (
                    (symbol.cx - s.cx) // 5,
                    0 if s.type == "chain" else 1,
                    symbol.cx - s.cx
                )
            )
            symbol.connected_with.append(best_left.symbol_id)
            
            if not getattr(best_left, 'connected_with', None):
                best_left.connected_with = []
            best_left.connected_with.append(symbol.symbol_id)

        # RIGHT SYMBOLS
        if right_candidates and not has_right:
            best_right = min(
                right_candidates,
                key=lambda s: (
                    (s.cx - symbol.cx) // 5,
                    0 if s.type == "chain" else 1,
                    s.cx - symbol.cx
                )
            )
            symbol.connected_with.append(best_right.symbol_id)
            
            if not getattr(best_right, 'connected_with', None):
                best_right.connected_with = []
            best_right.connected_with.append(symbol.symbol_id)

        return symbol.connected_with

    def _find_parent(self, symbol: CrochetSymbol, symbols: List[CrochetSymbol], target_x: float, target_y: float, search_width: float, search_depth: float) -> List[int]:
        """
        Uniwersal function to find parent one for: slip-stitch, crochet, hald-double-crochet
        """
        y_tolerance = symbol.height * 0.25

        candidates = [
            s for s in symbols 
            if s.symbol_id != symbol.symbol_id
            and getattr(s, 'is_connectable', True)
            and s.ymin > target_y 
            and s.ymin <= target_y + search_depth 
            and s.xmax >= target_x - search_width
            and s.xmin <= target_x + search_width
        ]
        
        if not candidates:
            return []

        best_candidate = min(
            candidates, 
            key=lambda s: (
                max(0, s.ymin - target_y) // max(5, symbol.height * 0.5),
                abs(s.cx - target_x), 
                s.ymin - target_y
            )
        )

        return [best_candidate.symbol_id]