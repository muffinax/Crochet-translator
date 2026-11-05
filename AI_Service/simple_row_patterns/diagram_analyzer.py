from crochet_symbol import CrochetSymbol
from typing import List, Dict, Any

class DiagramAnalyzer:
    def __init__(self, tolerance: float = 0.5):
        """
        Class analyzing rows, pattern boundaries, and starting points.
        :param tolerance: symbol center boundaries multiplier
        """
        self.tolerance = tolerance

    def _is_base_chain(self, symbol: CrochetSymbol) -> bool:
        if symbol.type != "chain":
            return False
        
        width = symbol.xmax - symbol.xmin
        height = symbol.ymax - symbol.ymin

        # if wrong detection
        if height == 0:
            return False
            
        # Aspect Ratio:
        # > 1.0 -> horizontal oval
        # == 1.0 -> circle
        # < 1.0 -> vertical oval
        aspect_ratio = width / height
        
        # returning only horizontal ovals and circles (base chains)
        return aspect_ratio >= 0.8

    def find_first_row(self, symbols: List[CrochetSymbol]) -> List[CrochetSymbol]:
        """
        Finding the first (base) row.
        :param symbols: list of detected symbols
        :return: list of symbols in the first row
        """
        base_chains = [s for s in symbols if self._is_base_chain(s)] 
        
        if not base_chains:
            return [] # There are no chains
            
        # Counting center of the chains
        chain_data = []
        for s in base_chains:
            cx, cy = s._get_center()
            h = s.ymax - s.ymin
            chain_data.append({"symbol": s, "cx": cx, "cy": cy, "h": h})
            
        # Looking for the lowest chain (highest Y value)
        lowest_chain = max(chain_data, key=lambda item: item["cy"])
        lowest_y = lowest_chain["cy"]
        
        # Counting average height
        avg_height = sum(item["h"] for item in chain_data) / len(chain_data)
        tolerance = avg_height * self.tolerance
        
        # Looking for chains in the same row within the tolerance
        first_row_data = [
            item for item in chain_data 
            if abs(item["cy"] - lowest_y) <= tolerance
        ]
        
        # Sorting chains from left to right
        first_row_data.sort(key=lambda item: item["cx"])
    
        return [item["symbol"] for item in first_row_data]

    def find_beginning(self, symbols: List[CrochetSymbol]) -> str:
        """
        Returns 'left' or 'right' depending on where the diagram starts.
        The start is on the opposite side of the lowest turning chain.
        """
        non_horizontal_chains = []
        all_cx = []

        for s in symbols:
            cx, _ = s._get_center()
            all_cx.append(cx)
            
            if s.type == "chain":
                width = s.xmax - s.xmin
                height = s.ymax - s.ymin
                if height > 0 and (width / height) < 0.8:
                    non_horizontal_chains.append(s)

        # Fallback: if there are no turning chains at all, assume left side
        if not non_horizontal_chains or not all_cx:
            return "left"

        # Find the lowest non-horizontal chain (highest Y value)
        lowest_chain = max(non_horizontal_chains, key=lambda s: s._get_center()[1])
        lowest_cx, _ = lowest_chain._get_center()

        # Determine the center of the entire diagram
        mid_x = (min(all_cx) + max(all_cx)) / 2.0

        # If the lowest turning chain is on the right side (X > middle), the pattern starts from the left
        if lowest_cx > mid_x:
            return "left"
        else:
            return "right"

    def find_rows_by_turning_chains(self, symbols: List[CrochetSymbol], base_row_symbols: List[CrochetSymbol] = None) -> Dict[str, Any]:
        """
        Calculates the number of rows based on the turning chains on the extreme sides.
        :param base_row_symbols: Symbols already identified as the base row (to exclude them).
        """
        if base_row_symbols is None:
            base_row_symbols = []
            
        vertical_chains = []
        all_cx = []

        # 1. Find potential turning chains (excluding base row)
        for s in symbols:
            cx, _ = s._get_center()
            all_cx.append(cx)
            
            # Zmiana: ignorujemy łańcuszki z zielonej ramki (rzędu bazowego)
            if s.type == "chain" and s not in base_row_symbols:
                width = s.xmax - s.xmin
                height = s.ymax - s.ymin
                if height > 0:
                    aspect_ratio = width / height
                    # Luźniejsza reguła: chwytamy pionowe (<0.8) ORAZ skośne przejściowe (~1.0 - 1.2)
                    if aspect_ratio < 1.3:
                        vertical_chains.append(s)

        if not vertical_chains or not all_cx:
            return {"row_count": 0, "row_chains": {}}

        min_x, max_x = min(all_cx), max(all_cx)
        pattern_width = max_x - min_x
        mid_x = (min_x + max_x) / 2.0
        
        left_boundary = min_x + (pattern_width * 0.3)
        right_boundary = max_x - (pattern_width * 0.3)

        edge_chains = [
            s for s in vertical_chains 
            if s._get_center()[0] <= left_boundary or s._get_center()[0] >= right_boundary
        ]

        if not edge_chains:
            edge_chains = vertical_chains

        # 4. Sort edge chains from the lowest visual point to the highest (descending Y)
        edge_chains.sort(key=lambda s: s._get_center()[1], reverse=True)

        row_groups = []
        current_group = []

        # 5. Group the chains vertically
        for chain in edge_chains:
            if not current_group:
                current_group.append(chain)
            else:
                last_chain = current_group[-1]
                dist_y = abs(chain._get_center()[1] - last_chain._get_center()[1])
                avg_h = ((chain.ymax - chain.ymin) + (last_chain.ymax - last_chain.ymin)) / 2.0
                
                chain_side = "left" if chain._get_center()[0] < mid_x else "right"
                last_chain_side = "left" if last_chain._get_center()[0] < mid_x else "right"

                # Tolerancję odległości możemy lekko zwiększyć do 3.0, by objąć skośny znak
                if chain_side == last_chain_side and dist_y <= (avg_h * 3.0):
                    current_group.append(chain)
                else:
                    row_groups.append(current_group)
                    current_group = [chain]

        if current_group:
            row_groups.append(current_group)

        row_chains_dict = {}
        for i, group in enumerate(row_groups):
            group.sort(key=lambda s: s._get_center()[1], reverse=True)
            row_chains_dict[i + 1] = group

        return {
            "row_count": len(row_groups),
            "row_chains": row_chains_dict
        }
    
    def extract_row_contents(
        self, 
        symbols: List[CrochetSymbol], 
        row_chains: Dict[int, List[CrochetSymbol]], 
        base_row_symbols: List[CrochetSymbol], 
        start_side: str
    ) -> Dict[int, List[CrochetSymbol]]:
        """
        Assigns symbols to rows based on the closest distance to the center of gravity 
        of the turning chains for a given row. Guarantees no duplicates.
        """
        row_contents = {r: [] for r in row_chains.keys()}
        
        # A set storing unique IDs of symbols that have already been assigned.
        # We use id() to solve the "unhashable type" error.
        assigned_ids = set()

        # 1. Secure the base row - mark them as "used"
        for s in base_row_symbols:
            assigned_ids.add(id(s))

        row_centers_y = {}

        # 2. Secure turning chains and calculate the "core" of the row
        for row_index, chains in row_chains.items():
            for c in chains:
                # Hard-assign turning chains to their respective rows
                row_contents[row_index].append(c)
                assigned_ids.add(id(c))
                
            # Calculate the average Y center (horizontal core of the row) based on turning chains
            if chains:
                avg_y = sum(c._get_center()[1] for c in chains) / len(chains)
                row_centers_y[row_index] = avg_y

        # 3. Assign remaining symbols (unreserved ones) to the CLOSEST row
        for s in symbols:
            # If the symbol is already in the base row or is a turning chain - ignore it
            if id(s) in assigned_ids:
                continue
                
            _, cy = s._get_center()
            
            closest_row = None
            min_dist = float('inf')
            
            # Find which row center is vertically closest to our symbol
            for row_index, center_y in row_centers_y.items():
                dist = abs(cy - center_y)
                if dist < min_dist:
                    min_dist = dist
                    closest_row = row_index
                    
            # Assign the symbol to the winning row
            if closest_row is not None:
                row_contents[closest_row].append(s)
                assigned_ids.add(id(s)) # Mark as used to keep things organized

        # 4. Sort the rows in the correct reading direction
        for row_index, current_row_symbols in row_contents.items():
            is_odd = (row_index % 2 != 0)
            
            if start_side == "left":
                sort_reverse = True if is_odd else False
            else: # start_side == "right"
                sort_reverse = False if is_odd else True

            current_row_symbols.sort(key=lambda s: s._get_center()[0], reverse=sort_reverse)
            row_contents[row_index] = current_row_symbols

        return row_contents