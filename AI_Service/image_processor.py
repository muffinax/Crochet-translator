import cv2
import numpy as np
from model.crochet_symbol import CrochetSymbol

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

    def get_bottom_binary(self, full_image: np.ndarray, symbol: CrochetSymbol):
        """Wyciąga dolną 1/3 symbolu i zwraca jej binarną maskę oraz koordynaty."""
        ymin, ymax = int(symbol.ymin), int(symbol.ymax)
        xmin, xmax = int(symbol.xmin), int(symbol.xmax)
        
        # Getting only 1/3 bootom part
        y_start = ymin + int(symbol.height * 0.66)
        
        roi = full_image[y_start:ymax, xmin:xmax]
        if roi.size == 0:
            return None, 0, 0

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        return binary, xmin, y_start

    def prepare_symbol(self, full_image: np.ndarray, symbol: CrochetSymbol, yframe: float = 0.1, xframe: float = 0.1):
        # Cropping the symbol from the original image
        ypad = int((symbol.ymax - symbol.ymin) * yframe)
        xpad = int((symbol.xmax - symbol.xmin) * xframe)
        ymin, ymax = max(0, symbol.ymin - ypad), min(full_image.shape[0], symbol.ymax + ypad)
        xmin, xmax = max(0, symbol.xmin - xpad), min(full_image.shape[1], symbol.xmax + xpad)
        
        # Region of Interest - roi
        roi = full_image[ymin:ymax, xmin:xmax]

        # Converting to grayscale and binarizing
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Isolating the main symbol
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        
        if num_labels == 0:
            return None, 0, 0 # Empty ROI (only background)

        # Finding the index of the largest object
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        
        # Creating a new, clean mask
        clean_binary = np.zeros_like(binary)
        # Drawing ONLY the largest object (our main stitch)
        clean_binary[labels == largest_label] = 255

        # Clearing random noises/pixels
        kernel = np.ones((2, 2), np.uint8)
        clean_binary = cv2.morphologyEx(clean_binary, cv2.MORPH_CLOSE, kernel)
        clean_binary = cv2.morphologyEx(clean_binary, cv2.MORPH_OPEN, kernel)

        # Add blur
        # clean_binary = cv2.GaussianBlur(clean_binary, (5, 5), 0)

        return clean_binary, xmin, ymin