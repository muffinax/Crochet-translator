import cv2
import random
import numpy as np
from typing import List

# Assuming these are imported correctly
from model.crochet_symbol import CrochetSymbol
from model.row import Row
from simple_row_patterns.diagram_analyzer import DiagramAnalyzer

class CrochetTester:
    def __init__(self, image: np.ndarray, symbols: List[CrochetSymbol], rows: List[Row], row_analyzer: DiagramAnalyzer):
        self.symbols = symbols
        self.rows = rows
        self.row_analyzer = row_analyzer

        self.debug_img = image.copy()
        
        self.type_colors = {
            "chain": (255, 200, 0),               
            "single-crochet": (0, 255, 0),        
            "slip-stitch": (0, 0, 255),           
            "slip-stich": (0, 0, 255),            
            "half-double-crochet": (255, 0, 255), 
            "crochet": (0, 255, 255),             
            "double-crochet": (0, 165, 255)       
        }

    # CONSOLE LOGGING

    def print_symbol_info(self):
        print("\n--- DETECTED SYMBOLS INFO ---")
        for s in self.symbols:
            conn = getattr(s, 'connected_with', [])
            base_str = " [BASE]" if getattr(s, 'is_base', False) else ""
            print(f"ID: {s.symbol_id} | Type: {s.type}{base_str} | "
                  f"Ratio: {s.ratio:.2f} | Size: {s.width}x{s.height} | "
                  f"Center: ({s.cx:.1f}, {s.cy:.1f}) | Connections: {conn}")

    def print_row_info(self):
        print("\n--- ROWS INFO ---")
        for row in self.rows:
            direction = "Left to Right" if row.is_reading_from_left else "Right to Left"
            symbol_types = [s.type for s in row.symbols]
            print(f"Row {row.row_id}: {len(row.symbols)} symbols | "
                  f"Reading: {direction} | Types: {symbol_types[:3]}...")

    def print_instructions(self):
        print("\n--- CROCHET INSTRUCTIONS ---")
        print(f"Total rows detected: {len(self.rows)}")
        if self.rows:
            start_side = "LEFT" if self.rows[0].is_reading_from_left else "RIGHT"
            print(f"Start reading the pattern from the {start_side} side.")
        print("\n[PLACEHOLDER] Generating instructions...")
        print("----------------------------\n")

    # VISUALIZATION LAYERS (Drawing on self.debug_img)
    
    def draw_type_colors(self):
        for symbol in self.symbols:
            pt1 = (int(symbol.xmin), int(symbol.ymin))
            pt2 = (int(symbol.xmax), int(symbol.ymax))
            color = self.type_colors.get(symbol.type, (128, 128, 128))
            cv2.rectangle(self.debug_img, pt1, pt2, color, 1)

    def draw_rows(self):
        assigned_ids = set()
        for row in self.rows:
            row_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            for symbol in row.symbols:
                assigned_ids.add(symbol.symbol_id)
                pt1 = (int(symbol.xmin), int(symbol.ymin))
                pt2 = (int(symbol.xmax), int(symbol.ymax))
                cv2.rectangle(self.debug_img, pt1, pt2, row_color, 2)
                
        for symbol in self.symbols:
            if symbol.symbol_id not in assigned_ids:
                pt1 = (int(symbol.xmin), int(symbol.ymin))
                pt2 = (int(symbol.xmax), int(symbol.ymax))
                cv2.rectangle(self.debug_img, pt1, pt2, (0, 0, 0), 1)

    def draw_lowest_points(self):
        for symbol in self.symbols:
            if symbol.type in ("crochet", "double-crochet", "half-double-crochet", "single-crochet"):
                lowest_pt = self.row_analyzer.symbol_analyzer.lowest_point(symbol)
                if lowest_pt:
                    lx, ly = lowest_pt
                    cv2.circle(self.debug_img, (int(lx), int(ly)), 2, (0, 0, 255), -1)

    def draw_base_symbols(self):
        for symbol in self.symbols:
            if getattr(symbol, 'is_base', False):
                pt1 = (int(symbol.xmin), int(symbol.ymin))
                pt2 = (int(symbol.xmax), int(symbol.ymax))
                cv2.rectangle(self.debug_img, pt1, pt2, (255, 0, 255), 2)

    def draw_connections(self):
        symbol_dict = {s.symbol_id: s for s in self.symbols}
        for symbol in self.symbols:
            if not getattr(symbol, 'connected_with', None):
                continue
                
            for parent_id in symbol.connected_with:
                if parent_id not in symbol_dict:
                    continue
                    
                parent_symbol = symbol_dict[parent_id]
                
                if symbol.type in ("crochet", "double-crochet", "half-double-crochet", "single-crochet"):
                    lowest_pt = self.row_analyzer.symbol_analyzer.lowest_point(symbol)
                    l1 = (int(lowest_pt[0]), int(lowest_pt[1])) if lowest_pt else (int(symbol.cx), int(symbol.cy))
                else:
                    l1 = (int(symbol.cx), int(symbol.cy))
                    
                l2 = (int(parent_symbol.cx), int(parent_symbol.cy))
                cv2.line(self.debug_img, l1, l2, (0, 255, 0), 2)

    # DISPLAY AND SAVE

    def save_image(self, filepath: str):
        """
        Saves the compiled image to a file. This is the BEST way to see 
        the true 100% quality of the bounding boxes and lines.
        """
        cv2.imwrite(filepath, self.debug_img)
        print(f"[VISUALIZER] Saved debug image to: {filepath}")

    def show_and_wait(self, window_name: str = "Crochet Debug"):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, self.debug_img)
        
        click_state = {"clicked": False}
        
        def close_on_click(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                param["clicked"] = True
                
        cv2.setMouseCallback(window_name, close_on_click, click_state)
        
        print(f"[{window_name}] Press any key or CLICK to continue (or 'q'/'ESC' to quit).")
        
        while True:
            key = cv2.waitKey(50) & 0xFF 
            if key in [27, ord('q'), ord('Q')]:
                cv2.destroyAllWindows()
                exit(0)
            elif key != 255:
                break
            elif click_state["clicked"]:
                break
                
        cv2.destroyWindow(window_name)