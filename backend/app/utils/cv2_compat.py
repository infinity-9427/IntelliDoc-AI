"""
OpenCV compatibility layer for handling system installations and providing fallbacks.
"""
import sys
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Try to import system OpenCV first
cv2 = None

try:
    # Try standard installation
    import cv2 as _cv2
    cv2 = _cv2
    logger.info("Using installed OpenCV package")
except ImportError:
    try:
        # Try system package locations
        sys.path.extend(['/usr/lib/python3/dist-packages', '/usr/local/lib/python3.12/site-packages'])
        import cv2 as _cv2
        cv2 = _cv2
        logger.info("Using system OpenCV package")
    except ImportError:
        logger.warning("OpenCV not available - using mock implementation")
        
        # Mock OpenCV implementation for basic compatibility
        class MockCV2:
            # Color conversion constants
            COLOR_BGR2GRAY = 6
            COLOR_RGB2GRAY = 7
            COLOR_BGR2RGB = 4
            
            # Threshold constants
            THRESH_BINARY = 0
            THRESH_OTSU = 8
            
            # Adaptive threshold constants
            ADAPTIVE_THRESH_MEAN_C = 0
            ADAPTIVE_THRESH_GAUSSIAN_C = 1
            
            # Morphology constants
            MORPH_RECT = 0
            MORPH_ELLIPSE = 1
            MORPH_CROSS = 2
            MORPH_CLOSE = 3
            MORPH_OPEN = 2
            MORPH_ERODE = 0
            MORPH_DILATE = 1
            
            def cvtColor(self, src, code):
                """Mock color conversion - returns input as-is"""
                logger.debug(f"Mock cvtColor called with code {code}")
                return src
            
            def fastNlMeansDenoising(self, src, dst=None, h=3, templateWindowSize=7, searchWindowSize=21):
                """Mock denoising - returns input as-is"""
                logger.debug("Mock fastNlMeansDenoising called")
                return src
            
            def adaptiveThreshold(self, src, maxValue, adaptiveMethod, thresholdType, blockSize, C):
                """Mock adaptive threshold - returns input as-is"""
                logger.debug("Mock adaptiveThreshold called")
                return src
            
            def threshold(self, src, thresh, maxval, type):
                """Mock threshold - returns dummy values"""
                logger.debug("Mock threshold called")
                return thresh, src
            
            def bilateralFilter(self, src, d, sigmaColor, sigmaSpace):
                """Mock bilateral filter - returns input as-is"""
                logger.debug("Mock bilateralFilter called")
                return src
            
            def createCLAHE(self, clipLimit=2.0, tileGridSize=(8,8)):
                """Mock CLAHE creation"""
                logger.debug("Mock createCLAHE called")
                class MockCLAHE:
                    def apply(self, src):
                        return src
                return MockCLAHE()
            
            def getStructuringElement(self, shape, ksize):
                """Mock structuring element - returns simple kernel"""
                logger.debug("Mock getStructuringElement called")
                return np.ones(ksize, np.uint8)
            
            def morphologyEx(self, src, op, kernel):
                """Mock morphology operation - returns input as-is"""
                logger.debug("Mock morphologyEx called")
                return src
        
        cv2 = MockCV2()
