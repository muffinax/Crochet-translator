import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from crochet_symbol import CrochetSymbol

class SymbolDetector:
    def __init__(self, model_path: str = 'my_model/my_model.pt'):
        """
        Initialize the SymbolDetector with the YOLO model.
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        self.model = YOLO(self.model_path, task='detect')
        self.labels = self.model.names

    def detect_symbols(self, image):
        """
        Detect symbols in the provided image using the YOLO model.
        :param image: Input image in which to detect symbols.
        :return: Detection results from the YOLO model.
        """
        min_thresh = 0.5  # Minimum confidence threshold for displaying detected objects

        # Check if the input is a file path or a numpy array
        if isinstance(image, (str, Path)):
            frame = cv2.imread(str(image))
            if frame is None:
                raise ValueError(f"Could not read image from {image}")
        elif isinstance(image, np.ndarray):
            frame = image
        else:
            raise TypeError("Input must be a file path or a numpy array representing an image.")

        # Perform detection using the YOLO model
        results = self.model(frame, conf=min_thresh, verbose=False)
        detections = results[0].boxes

        print(f"{detected_objects[0].type} detected with confidence {detected_objects[0].confidence} at coordinates ({detected_objects[0].xmin}, {detected_objects[0].ymin}), ({detected_objects[0].xmax}, {detected_objects[0].ymax})")


        detected_objects = []

        # Iterate through the detected boxes and create CrochetSymbol instances
        for box in detections:
            xyxy = box.xyxy.cpu().numpy().squeeze()
            xmin, ymin, xmax, ymax = xyxy.astype(int)
            
            classidx = int(box.cls.item())
            classname = self.labels[classidx]
            conf = box.conf.item()

            symbol = CrochetSymbol(
                type=classname, 
                xmin=int(xmin), ymin=int(ymin), xmax=int(xmax), ymax=int(ymax), 
                confidence=round(float(conf), 2)
            )
            detected_objects.append(symbol)
        
        return detected_objects