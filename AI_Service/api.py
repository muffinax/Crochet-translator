import cv2
import tempfile
import uvicorn
import numpy as np
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import Twojej funkcji uruchamiającej z maina
from main import process_crochet_diagram

app = FastAPI(title="Crochet Translator API")

# Bardzo ważne dla Reacta! Konfiguracja CORS pozwala frontendowi z innego portu pytać backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = 'my_model/my_model.pt'

@app.post("/api/translate")
async def translate_diagram(file: UploadFile = File(...)):
    """
    Endpoint gets image and returns instruction
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Przesłany plik nie jest obrazem.")

    # Odczyt pliku prosto do pamięci (żeby nie pisać na dysk, jeśli to niepotrzebne)
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        arr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if arr is None:
             raise ValueError("Nie udało się zdekodować obrazu.")
             
    except Exception as e:
         raise HTTPException(status_code=422, detail=f"Błąd odczytu pliku: {str(e)}")

    # Uruchomienie Twojego potężnego pipeline'u
    try:

        instructions_dict = process_crochet_diagram(
            arr=arr,
            model_path=MODEL_PATH,
            debug_mode=False
        )

        output_lines = []
        for row_data in instructions_dict.get("pattern", []):
            output_lines.append(f"R{row_data['row_id']}: {row_data['text']}")
            
        final_text = "\n".join(output_lines)
        
        # Zwracamy obiekt JSON, z którego React wyciągnie sobie pole 'text'
        return {"status": "success", "text": final_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wewnętrzny błąd analizatora: {str(e)}")


if __name__ == "__main__":
    # Odpalanie serwera deweloperskiego na porcie 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)