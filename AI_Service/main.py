import cv2
from pathlib import Path

from symbol_detector import SymbolDetector
from image_processor import ImageProcessor
from simple_row_patterns.diagram_analyzer import DiagramAnalyzer

if __name__ == "__main__":
    # 1. Initialization of the modules
    detector = SymbolDetector(model_path='my_model/my_model.pt')
    imageprocessor = ImageProcessor()
    analyzer = DiagramAnalyzer()

    # Define image path and read image
    image_path = Path(r'D:\Projects\Data-AI\Crochet\test-files\basic\test-01.png')
    image = cv2.imread(str(image_path))

    # Preprocess image and detect symbols
    # arr = imageprocessor.sharpen(image)
    arr = imageprocessor.enhance_faint_lines(image)
    detected_symbols = detector.detect_symbols(arr)

    # # Analyze the diagram
    # # Base row (Row 0) and start side
    # base_row_symbols = analyzer.find_first_row(detected_symbols)
    # start_side = analyzer.find_beginning(detected_symbols)
    
    # # Turning chains and row counting
    # rows_data = analyzer.find_rows_by_turning_chains(detected_symbols, base_row_symbols)
    # row_count = rows_data["row_count"]
    # row_chains = rows_data["row_chains"]

    # # Getting all rows with proper direction
    # row_contents = analyzer.extract_row_contents(
    #     symbols=detected_symbols,
    #     row_chains=row_chains,
    #     base_row_symbols=base_row_symbols,
    #     start_side=start_side
    # )

    # print(f"Diagram starts on the: {start_side.upper()} side")
    # print(f"Elements in base row (Row 0): {len(base_row_symbols)}")
    # for r_idx, content in row_contents.items():
    #     print(f"Row {r_idx}: found {len(content)} symbols.")

    # VISUALIZATION
    colors = [(0, 0, 255), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 165, 255), (0, 255, 255)]

    type_colors = {}
    color_index = 0

    for symbol in detected_symbols:
        if symbol.type not in type_colors:
            type_colors[symbol.type] = colors[color_index % len(colors)]
            color_index += 1
            
        color = type_colors[symbol.type]

        start_point = (int(symbol.xmin), int(symbol.ymin))
        end_point = (int(symbol.xmax), int(symbol.ymax))
        
        cv2.rectangle(arr, start_point, end_point, color, 2)
        
        text_x = int(symbol.xmin)
        text_y = int(symbol.ymin) - 5

        if text_y < 10: 
            text_y = int(symbol.ymax) + 15
            
        cv2.putText(
            arr, 
            symbol.type, 
            (text_x, text_y), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.4, 
            color, 
            1
        )

    print("Types and their colours (BGR):")
    for sym_type, col in type_colors.items():
        print(f"- {sym_type}: {col}")

    # # Draw base row (Row 0) with GREEN rectangles
    # for symbol in base_row_symbols:
    #     start_point = (int(symbol.xmin), int(symbol.ymin))
    #     end_point = (int(symbol.xmax), int(symbol.ymax))
    #     cv2.rectangle(arr, start_point, end_point, (0, 255, 0), 2)
        
    # # Draw all symbols assigned to specific rows
    # for row_index, symbols_in_row in row_contents.items():
    #     color = colors[(row_index - 1) % len(colors)] 
        
    #     # Iterate over all symbols in the current row
    #     for i, symbol in enumerate(symbols_in_row):
    #         start_point = (int(symbol.xmin), int(symbol.ymin))
    #         end_point = (int(symbol.xmax), int(symbol.ymax))
            
    #         # Draw bounding box for the symbol
    #         cv2.rectangle(arr, start_point, end_point, color, 2)
            
    #         # Add text label indicating the order (e.g., "R1: 1", "R1: 2") to verify direction
    #         text_x = int(symbol.xmin)
    #         text_y = int(symbol.ymin) - 5
            
    #         # Only draw text for the turning chains to avoid visual clutter, 
    #         # or for all if you want to see the reading order. Let's draw just "R{row_index}" 
    #         cv2.putText(
    #             arr, 
    #             f"R{row_index}", 
    #             (text_x, text_y), 
    #             cv2.FONT_HERSHEY_SIMPLEX, 
    #             0.4, 
    #             color, 
    #             1
    #         )

    cv2.imshow("Diagram Analysis - Full Rows", arr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()