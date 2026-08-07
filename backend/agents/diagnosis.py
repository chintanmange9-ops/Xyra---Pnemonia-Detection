import os
import torch
import torch.nn as nn
import numpy as np
from torchvision import models

import config


class DiagnosisAgent:
    """Single 3-class pneumonia classifier.

    EfficientNet-B2 @384px: NORMAL / BACTERIAL / VIRAL
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.model_loaded = False
        self.model_version = "EfficientNet-B2_384px_3class_v1.0"
        self._load_model()

    def _make_model(self, num_classes=3):
        """Build EfficientNet-B2 with custom classifier head (matches training)."""
        m = models.efficientnet_b2(weights=None)
        in_features = m.classifier[1].in_features
        m.classifier = nn.Sequential(nn.Dropout(0.3), nn.Linear(in_features, num_classes))
        return m

    def _load_model(self):
        try:
            model = self._make_model(num_classes=len(config.MODEL_CLASSES))
            if os.path.exists(config.MODEL_WEIGHTS):
                state_dict = torch.load(
                    config.MODEL_WEIGHTS, map_location=self.device, weights_only=True
                )
                model.load_state_dict(state_dict)
                print(f"[DiagnosisAgent] Model loaded from {config.MODEL_WEIGHTS}")
            else:
                print(f"[DiagnosisAgent] WARNING: No weights at {config.MODEL_WEIGHTS}")
            model.to(self.device)
            model.eval()
            self.model = model
            self.model_loaded = True
        except Exception as e:
            print(f"[DiagnosisAgent] Model load failed: {e}")

    def run(self, preprocessed_image: np.ndarray) -> dict:
        """Classify chest X-ray: NORMAL / BACTERIAL / VIRAL."""
        if not self.model_loaded:
            return {
                "label": "Unknown",
                "confidence_score": 0.0,
                "model_version": "not_loaded",
                "logits": [0.0] * len(config.MODEL_CLASSES),
                "probabilities": {},
            }

        tensor = torch.from_numpy(preprocessed_image).unsqueeze(0)
        tensor = tensor.to(self.device, dtype=self.model.classifier[1].weight.dtype)

        with torch.no_grad():
            output = self.model(tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        label = config.MODEL_CLASSES[predicted.item()]
        conf = confidence.item()
        logits = probabilities[0].cpu().tolist()
        probs_dict = {cls: round(prob, 4) for cls, prob in zip(config.MODEL_CLASSES, logits)}

        result = {
            "label": label,
            "confidence_score": round(conf, 4),
            "model_version": self.model_version,
            "logits": [round(l, 4) for l in logits],
            "probabilities": probs_dict,
        }
        return result
