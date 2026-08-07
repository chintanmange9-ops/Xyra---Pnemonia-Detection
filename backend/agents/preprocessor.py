import cv2
import numpy as np
from PIL import Image
import config


class PreprocessingAgent:
    """Module 1: Input preprocessing — RGB + ImageNet normalization (matches EfficientNet training)."""

    def __init__(self, target_size=(384, 384)):
        self.target_size = target_size

    def run(self, image: Image.Image) -> np.ndarray:
        img_array = np.array(image)

        resized = cv2.resize(img_array, self.target_size, interpolation=cv2.INTER_LANCZOS4)

        normalized = resized.astype(np.float32) / 255.0
        mean = np.array(config.IMAGENET_MEAN)
        std = np.array(config.IMAGENET_STD)
        normalized = (normalized - mean) / std

        return normalized.transpose(2, 0, 1)

    def get_clahe_image(self, image: Image.Image) -> np.ndarray:
        """Return CLAHE-enhanced image for visualization (not used in main pipeline)."""
        img_array = np.array(image)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def augment(self, image: Image.Image, rotation_deg=15) -> Image.Image:
        """Data augmentation for low-confidence retry loop (not used in main pipeline)."""
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        import random
        angle = random.uniform(-rotation_deg, rotation_deg)
        h, w = gray.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(gray, matrix, (w, h))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(rotated)
        if len(img_array.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(enhanced)
