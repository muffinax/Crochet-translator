from symbol_detector import SymbolDetector
from pathlib import Path

if __name__ == "__main__":
    detector = SymbolDetector(model_path='my_model/my_model.pt')

    image_path = Path(r'D:\GitHub\Crochet-translator\AI_Service\dataset\images\f77cfb8f-Zrzut_ekranu_2026-10-26_234131.png')
    
    detected_symbols = detector.detect_symbols(image_path)