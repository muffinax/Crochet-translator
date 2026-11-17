import cv2
import json
import sys
from pathlib import Path
import numpy as np

# Importy Twoich klas
from symbol_detector import SymbolDetector
from simple_row_patterns.row_analyzer import RowAnalyzer
from simple_row_patterns.diagram_analyzer import DiagramAnalyzer
from instruction_generator import InstructionGenerator
from crochet_tester import CrochetTester

def process_crochet_diagram(arr: np.ndarray, model_path: str, debug_mode: bool = False, path_obj: Path = None) -> dict:
    """
    main Pipeline - JSON
    """
    # Inicialization
    detector = SymbolDetector(model_path=model_path)
    diagram_analyzer = RowAnalyzer()
    row_analyzer = DiagramAnalyzer(arr)
    instruction_generator = InstructionGenerator()

    # Symbol Detection
    detected_symbols = detector.detect_symbols(arr)
    if not detected_symbols:
        return {"pattern": [], "message": "No symbols detected."}

    # Preaparing data
    base_row, edge_groups = row_analyzer.prepare_base_symbols(detected_symbols)
    detected_symbols = row_analyzer.locate_symbols(detected_symbols)

    # Building Rows Structure
    result_rows = diagram_analyzer.build_rows(detected_symbols, base_row, edge_groups)

    # Generating instruction
    instructions_dict = instruction_generator.generate_instructions(result_rows)

    if debug_mode:
        tester = CrochetTester(arr, detected_symbols, result_rows, row_analyzer)
        
        tester.print_symbol_info()
        tester.print_row_info()
        
        tester.draw_rows()
        tester.draw_base_symbols()
        tester.draw_lowest_points()
        tester.draw_connections()
        
        if path_obj:
            debug_filepath = str(path_obj.parent / f"debug_{path_obj.name}")
            tester.save_image(debug_filepath)
            tester.show_and_wait(f"Debug: {path_obj.name}")
        else:
            tester.save_image("debug_output.png")
            tester.show_and_wait("Debug: output")

    return instructions_dict


# Lokal test
if __name__ == "__main__":
    MODEL_PATH = 'my_model/my_model.pt'
    BASE_DIR = Path(r'D:\Projects\Data-AI\Crochet\test-files\basic')

    for i in range(1, 14):
        filename = f'test-{i:02d}.png'
        img_path = BASE_DIR / filename
        
        if not img_path.exists():
            print(f"Skipping {filename} - file not found.")
            continue
            
        print(f"\n{'='*40}\nProcessing: {filename}\n{'='*40}")
        
        try:
            image_array = cv2.imread(str(img_path))
            if image_array is None:
                print(f"Failed to load image: {filename}", file=sys.stderr)
                continue

            output_json = process_crochet_diagram(
                arr=image_array, 
                model_path=MODEL_PATH, 
                debug_mode=True,
                path_obj=img_path
            )
            
            # save JSON
            json_filename = BASE_DIR / f"instructions_{img_path.stem}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(output_json, f, indent=4, ensure_ascii=False)
                
            print(f"Successfully saved JSON to: {json_filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)

    cv2.destroyAllWindows()