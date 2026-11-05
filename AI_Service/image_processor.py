import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, default_max_size: int = 800):
        """
        Preparing image before using YOLO model
        :param default_max_size: max sizeof the longer side of an image (for YOLO model max is 640 - but it can automatically scale)
        """
        self.default_max_size = default_max_size
    
    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """
        Sharpens the image for better detection results
        :param image: Input image to prepare for YOLO detection.
        """
        kernel = np.array([[ 0, -1,  0],
                           [-1,  5, -1],
                           [ 0, -1,  0]])
        return cv2.filter2D(image, -1, kernel)
    
    def enhance_faint_lines(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale - YOLO usually expects RGB/BGR inputs (but required for edge and threshold analysis)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding to extract shapes regardless of background brightness
        thresh = cv2.adaptiveThreshold(
            gray, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 
            2
        )
        
        # Converting the single-channel binary image back to BGR.
        enhanced = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        
        return enhanced