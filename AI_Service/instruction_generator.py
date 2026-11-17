import json
from collections import Counter
from typing import List, Dict, Any
from model.crochet_symbol import CrochetSymbol
from model.row import Row

class InstructionGenerator:
    def __init__(self):
        pass

    def generate_instructions(self, rows: List[Row]) -> Dict[str, Any]:
        """
        Main function to analyze rows and generate structural instructions.
        Returns a dictionary that can be easily converted to JSON for a web app.
        """
        instructions_data = {"pattern": []}
        text_instructions = []

        for i, row in enumerate(rows):
            # Row 0
            if i == 0:
                base_text = self._process_base_row(row)
                text_instructions.append(f"R{row.row_id}: {base_text}")
                instructions_data["pattern"].append({
                    "row_id": row.row_id,
                    "text": base_text,
                    "type": "base"
                })
                continue

            previous_row = rows[i-1]
            
            # Basic grouping (Run-Length Encoding)
            grouped_symbols = self._group_identical_symbols(row.symbols)
            
            # Find repeating sequences (Patterns)
            pattern_blocks = self._find_repeating_patterns(grouped_symbols)
            
            # Determine insertion points (loops) based on parent connections
            self._determine_insertion_points(pattern_blocks, previous_row)
            
            # Generate human-readable text
            row_text = self._format_row_text(pattern_blocks)
            text_instructions.append(f"R{row.row_id}: {row_text}")
            
            instructions_data["pattern"].append({
                "row_id": row.row_id,
                "text": row_text,
                "blocks": pattern_blocks,
                "type": "regular"
            })

        # Print to console for debugging
        print("\n--- GENERATED INSTRUCTIONS ---")
        for text in text_instructions:
            print(text)
            
        return instructions_data

    def _process_base_row(self, row: Row) -> str:
        """
        Base row is usually just a starting chain.
        """
        if not row.symbols:
            return "Empty"
        
        counts = Counter([s.type for s in row.symbols])
        parts = [f"{count} {sym_type}" for sym_type, count in counts.items()]
        return ", ".join(parts)

    def _group_identical_symbols(self, symbols: List[CrochetSymbol]) -> List[Dict]:
        """
        Groups adjacent symbols of the same type (e.g., 3 chains in a row).
        """
        if not symbols:
            return []

        grouped = []
        current_type = symbols[0].type
        current_group = [symbols[0]]

        for s in symbols[1:]:
            if s.type == current_type:
                current_group.append(s)
            else:
                grouped.append({
                    "type": current_type,
                    "count": len(current_group),
                    "symbols": current_group
                })
                current_type = s.type
                current_group = [s]

        # Add the last group
        grouped.append({
            "type": current_type,
            "count": len(current_group),
            "symbols": current_group
        })

        return grouped

    def _find_repeating_patterns(self, grouped_symbols: List[Dict]) -> List[Dict]:
        """
        Basic pattern matching. Looks for repeating sequences of groups.
        (e.g., [2 chain, 1 crochet, 2 chain, 1 crochet] -> 2 repeats of [2 chain, 1 crochet])
        """
        n = len(grouped_symbols)
        if n < 4: 
            # Too short to find meaningful repeating patterns, return as plain sequence
            return [{"repeat": 1, "sequence": [g]} for g in grouped_symbols]

        final_blocks = []
        i = 0
        
        while i < n:
            best_repeat = 1
            best_seq_len = 1
            
            # Check for patterns of length 1 up to n/2
            for seq_len in range(1, (n - i) // 2 + 1):
                repeats = 1
                # Compare current window with the next window
                while i + (repeats + 1) * seq_len <= n:
                    window1 = grouped_symbols[i + repeats * seq_len - seq_len : i + repeats * seq_len]
                    window2 = grouped_symbols[i + repeats * seq_len : i + (repeats + 1) * seq_len]
                    
                    # Compare types and counts
                    match = all(w1["type"] == w2["type"] and w1["count"] == w2["count"] 
                                for w1, w2 in zip(window1, window2))
                    if match:
                        repeats += 1
                    else:
                        break
                
                if repeats > best_repeat:
                    best_repeat = repeats
                    best_seq_len = seq_len

            if best_repeat > 1:
                # Found a repeating pattern!
                final_blocks.append({
                    "repeat": best_repeat,
                    "sequence": grouped_symbols[i : i + best_seq_len]
                })
                i += best_repeat * best_seq_len
            else:
                # No pattern, just add the single element
                final_blocks.append({
                    "repeat": 1,
                    "sequence": [grouped_symbols[i]]
                })
                i += 1

        return final_blocks

    def _determine_insertion_points(self, pattern_blocks: List[Dict], previous_row: Row):
        """
        Determines where the stitches are inserted into the previous row.
        Uses majority voting if a sequence repeats.
        """
        prev_symbols_ids = {s.symbol_id: idx for idx, s in enumerate(previous_row.symbols)}

        for block in pattern_blocks:
            # We will calculate relative insertion points for the sequence
            sequence = block["sequence"]
            
            for seq_item in sequence:
                insertion_offsets = []
                
                # Check all instances of this item in the repeat block to find the consensus
                for sym in seq_item["symbols"]:
                    parents = getattr(sym, 'connected_with', [])
                    if not parents:
                        continue
                        
                    # Find where the parent is located in the previous row
                    parent_indices = [prev_symbols_ids[p_id] for p_id in parents if p_id in prev_symbols_ids]
                    
                    if parent_indices:
                        # Take the average parent index if connected to multiple
                        avg_parent_idx = int(sum(parent_indices) / len(parent_indices))
                        insertion_offsets.append(avg_parent_idx)

                # Majority voting: what is the most common relative step?
                if insertion_offsets:
                    # note if it skips loops.
                    most_common = Counter(insertion_offsets).most_common(1)[0][0]
                    seq_item["insert_info"] = "specific loops based on connections" # Placeholder for complex relative math
                else:
                    seq_item["insert_info"] = "in space/chain"

    def _format_row_text(self, pattern_blocks: List[Dict]) -> str:
        """
        Converts the structured blocks into a human-readable crochet string.
        """
        parts = []
        for block in pattern_blocks:
            seq_strs = []
            for item in block["sequence"]:
                seq_strs.append(f"{item['count']} {item['type']}")
            
            seq_text = ", ".join(seq_strs)
            
            if block["repeat"] > 1:
                # Calculate loops covered (mocked up based on prompt)
                parts.append(f"repeat ({seq_text}) {block['repeat']} times")
            else:
                parts.append(seq_text)

        return ", ".join(parts)