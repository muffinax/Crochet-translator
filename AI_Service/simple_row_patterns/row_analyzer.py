from model.crochet_symbol import CrochetSymbol
from model.row import Row, reset_row_ids
from typing import List

class RowAnalyzer:
    def build_rows(self, symbols: List[CrochetSymbol], base_row: List[CrochetSymbol], edge_groups: List[List[CrochetSymbol]]) -> List[Row]:
        """
        Creates Rows
        """
        if not base_row:
            return []

        reset_row_ids()
        rows: List[Row] = []
        
        # Creating base -> row 0 + row transitions
        row_0 = Row(symbols=base_row, is_reading_from_left=True)
        rows.append(row_0)
        
        side_left = True
        
        if len(edge_groups) >= 2:
            if edge_groups[0][0].cx > edge_groups[1][0].cx:
                side_left = True
            else:
                side_left = False
        elif len(edge_groups) == 1:
            center_x = sum(s.cx for s in base_row) / len(base_row)
            side_left = edge_groups[0][0].cx < center_x

        for group in edge_groups:
            rows.append(Row(symbols=group, is_reading_from_left=side_left))
            side_left = not side_left

        symbol_row_map = {s.symbol_id: r.row_id for r in rows for s in r.symbols}
        unassigned = [s for s in symbols if s.symbol_id not in symbol_row_map]

        # 2. DWIE LISTY: Znane powiązania oraz Sieroty
        connected_queue = [s for s in unassigned if getattr(s, 'connected_with', [])]
        orphans = [s for s in unassigned if not getattr(s, 'connected_with', [])]

        # 3. KOLEJKA POWIĄZAŃ (BFS od dołu)
        changed = True
        while connected_queue and changed:
            changed = False
            remaining = []

            for symbol in connected_queue:
                parents = getattr(symbol, 'connected_with', [])
                parent_rows = [symbol_row_map.get(p_id) for p_id in parents]
                
                if all(pr is not None for pr in parent_rows):
                    highest_parent_row = max(parent_rows)
                    
                    # LOGIKA SZYDEŁKOWA: Chain w tym samym rzędzie, reszta wyżej
                    if symbol.type == "chain":
                        target_row_id = highest_parent_row
                    else:
                        target_row_id = highest_parent_row + 1
                        
                    # DYNAMICZNE DODAWANIE RZĘDÓW (jeśli szkielet był za krótki)
                    while len(rows) <= target_row_id:
                        last_side = rows[-1].is_reading_from_left
                        rows.append(Row(symbols=[], is_reading_from_left=not last_side))
                        
                    rows[target_row_id].symbols.append(symbol)
                    symbol_row_map[symbol.symbol_id] = target_row_id
                    changed = True
                else:
                    # Rodzice jeszcze nie mają rzędu, czekamy
                    remaining.append(symbol)

            connected_queue = remaining

        # Jeśli cokolwiek zostało w connected_queue (błędne cykle powiązań), traktujemy to jako sieroty
        orphans.extend(connected_queue)

        # 4. PRZYPISYWANIE SIEROT
        for symbol in orphans:
            # Sierota szuka TYLKO wśród symboli, które mają już pewny rząd
            assigned_symbols = [s for s in symbols if s.symbol_id in symbol_row_map]
            
            if assigned_symbols:
                closest_neighbor = min(
                    assigned_symbols,
                    key=lambda s: abs(s.cy - symbol.cy)
                )
                target_row_id = symbol_row_map[closest_neighbor.symbol_id]
                
                rows[target_row_id].symbols.append(symbol)
                symbol_row_map[symbol.symbol_id] = target_row_id
            else:
                # Fallback absolutny
                rows[0].symbols.append(symbol)

        # 5. BEZPIECZNE SORTOWANIE (is_base nienaruszone)
        for r in rows:
            base_syms = [s for s in r.symbols if getattr(s, 'is_base', False)]
            regular_syms = [s for s in r.symbols if not getattr(s, 'is_base', False)]

            if r.is_reading_from_left:
                regular_syms.sort(key=lambda s: s.cx)
            else:
                regular_syms.sort(key=lambda s: s.cx, reverse=True)

            r.symbols = base_syms + regular_syms

        return rows