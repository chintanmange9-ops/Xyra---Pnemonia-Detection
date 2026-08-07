import os
import time
import uuid
import numpy as np
import torch
import cv2
from PIL import Image

import config

ATTR_SIZE = (256, 256)  # Integrated Gradients runs at this resolution (cheaper), then upscaled for display


class ExplainabilityAgent:
    """Module 3: Grad-CAM and Integrated Gradients for 3-class model."""

    def __init__(self, diagnosis_model=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.diagnosis_model = diagnosis_model
        self.target_layer = None
        self._unet_model = None
        self._unet_device = None

        if diagnosis_model is not None:
            self._setup_target_layer()
        self._load_unet()

    def _setup_target_layer(self):
        model = self._get_active_model()
        if model is not None:
            # For EfficientNet-B2, use features[7] (last MBConv block) for better spatial localization
            if hasattr(model.features, '__getitem__') and len(model.features) >= 8:
                self.target_layer = model.features[7]
                print(f"[ExplainabilityAgent] Target layer set: model.features[7] (MBConv block)")
            else:
                self.target_layer = model.features
                print(f"[ExplainabilityAgent] Target layer set: model.features")
        else:
            print("[ExplainabilityAgent] No model available for target layer setup")

    def _load_unet(self):
        """Load the trained U-Net lung segmentation model (efficientnet-b0 backbone)."""
        try:
            import segmentation_models_pytorch as smp
            unet_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                "best_unet_model.pth",
            )
            if not os.path.exists(unet_path):
                print(f"[ExplainabilityAgent] U-Net not found at {unet_path}, using OpenCV fallback")
                return
            model = smp.Unet(encoder_name="efficientnet-b0", encoder_weights=None, in_channels=1, classes=1)
            sd = torch.load(unet_path, map_location=self.device, weights_only=True)
            model.load_state_dict(sd)
            model.eval()
            self._unet_model = model
            self._unet_device = self.device
            print(f"[ExplainabilityAgent] U-Net loaded from {unet_path}")
        except Exception as e:
            print(f"[ExplainabilityAgent] U-Net load failed ({e}), using OpenCV fallback")

    def _preprocess(self, image: Image.Image, size=None):
        """Preprocess image: RGB + ImageNet normalization (matches training)."""
        img_array = np.array(image)

        resized = cv2.resize(img_array, size or config.MODEL_INPUT_SIZE, interpolation=cv2.INTER_LANCZOS4)

        normalized = resized.astype(np.float32) / 255.0
        mean = np.array(config.IMAGENET_MEAN)
        std = np.array(config.IMAGENET_STD)
        normalized = (normalized - mean) / std

        input_tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0).float()

        return input_tensor, img_array

    def run_fast(self, original_image: Image.Image, case_id: str | None = None, predicted_class: int = 0) -> dict:
        """Run Grad-CAM + IntegratedGradients."""
        if case_id is None:
            case_id = f"PX-{uuid.uuid4().hex[:5].upper()}"

        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

        result = {
            "case_id": case_id,
            "grad_cam_url": None,
            "shap_url": None,
            "shap_analysis": [],
        }

        grad_cam_path = self._generate_gradcam(original_image, case_id, predicted_class)
        if grad_cam_path:
            result["grad_cam_url"] = f"/static/outputs/{os.path.basename(grad_cam_path)}"

        shap_result = self._generate_shap(original_image, case_id, predicted_class)
        if shap_result:
            shap_path, shap_analysis = shap_result
            result["shap_url"] = f"/static/outputs/{os.path.basename(shap_path)}"
            result["shap_analysis"] = shap_analysis

        return result

    def _get_active_model(self):
        """Return the active diagnosis model."""
        if self.diagnosis_model is None:
            return None
        if self.diagnosis_model.model_loaded:
            return self.diagnosis_model.model
        return None

    def _generate_gradcam(self, image: Image.Image, case_id: str, target_class: int = 0) -> str | None:
        try:
            from pytorch_grad_cam import GradCAMPlusPlus
            from pytorch_grad_cam.utils.image import show_cam_on_image
            from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

            model = self._get_active_model()
            if model is None:
                print("[GradCAM++] No model available, skipping")
                return None

            # Use features[7] (MBConv block) for better spatial localization
            if hasattr(model.features, '__getitem__') and len(model.features) >= 8:
                target_layers = [model.features[7]]
            else:
                target_layers = [model.features]

            input_tensor, img_array = self._preprocess(image)

            with torch.no_grad():
                output = model(input_tensor)
                pred_class = output.argmax(dim=1).item()

            cam = GradCAMPlusPlus(model=model, target_layers=target_layers)
            targets = [ClassifierOutputTarget(pred_class)]

            grayscale_cam = cam(input_tensor=input_tensor, targets=targets)  # pyright: ignore[reportArgumentType]  (grad-cam stub types targets as List[Module])

            with torch.no_grad():
                class_list = config.MODEL_CLASSES
                pred_label = class_list[pred_class] if pred_class < len(class_list) else f"Class {pred_class}"
                pred_conf = torch.softmax(model(input_tensor), dim=1)[0][pred_class].item()
            grayscale_cam = grayscale_cam[0]

            display_array = np.array(image.convert("RGB"))
            display_rgb = cv2.resize(display_array, config.MODEL_INPUT_SIZE)
            original_for_overlay = display_rgb.astype(np.float32) / 255.0
            cam_image = show_cam_on_image(original_for_overlay, grayscale_cam, use_rgb=True)

            output_path = os.path.join(config.OUTPUT_DIR, f"{case_id}_gradcam.png")
            cv2.imwrite(output_path, cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR))
            print(f"[GradCAM++] Saved to {output_path} (class={pred_label}, conf={pred_conf:.1%})")
            return output_path

        except ImportError:
            print("[GradCAM++] grad-cam library not installed, skipping")
            return None
        except Exception as e:
            print(f"[GradCAM++] Error: {e}")
            return None

    def _build_lung_mask(self, image_rgb: np.ndarray) -> np.ndarray:
        """Lung-field mask: U-Net segmentation (preferred) or OpenCV fallback."""
        if self._unet_model is not None:
            return self._unet_lung_mask(image_rgb)
        return self._opencv_lung_mask(image_rgb)

    def _unet_lung_mask(self, image_rgb: np.ndarray) -> np.ndarray:
        """Precise lung mask using the trained U-Net (efficientnet-b0 backbone, 512px)."""
        UNET_SIZE = 512
        MEAN, STD = 0.48732, 0.24189
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, (UNET_SIZE, UNET_SIZE)).astype(np.float32) / 255.0
        normed = (resized - MEAN) / STD
        tensor = torch.from_numpy(normed).unsqueeze(0).unsqueeze(0).float().to(self._unet_device)
        with torch.no_grad():
            pred = torch.sigmoid(self._unet_model(tensor)).squeeze().cpu().numpy()
        mask_small = (pred > 0.5).astype(np.uint8)
        mask_full = cv2.resize(mask_small, (image_rgb.shape[1], image_rgb.shape[0]),
                               interpolation=cv2.INTER_NEAREST).astype(bool)
        if mask_full.sum() < 0.03 * mask_full.size:
            print("[Attribution] U-Net mask too small, using OpenCV fallback")
            return self._opencv_lung_mask(image_rgb)
        return mask_full

    def _opencv_lung_mask(self, image_rgb: np.ndarray) -> np.ndarray:
        """Fallback: heuristic lung mask via Otsu + percentile thresholding."""
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        blur7 = cv2.GaussianBlur(gray, (7, 7), 0)

        _, body_raw = cv2.threshold(blur7, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        k15 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        body = cv2.morphologyEx(body_raw, cv2.MORPH_CLOSE, k15)
        body = cv2.morphologyEx(body, cv2.MORPH_OPEN, k15)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(body, connectivity=8)
        if n >= 2:
            best = max(range(1, n), key=lambda i: stats[i, cv2.CC_STAT_AREA])
            body = (labels == best).astype(np.uint8) * 255

        heavy = cv2.GaussianBlur(gray, (41, 41), 0)
        body_pixels = np.asarray(heavy[body > 0], dtype=np.float64)
        if len(body_pixels) == 0:
            return np.ones(gray.shape, dtype=bool)
        thresh = float(np.percentile(body_pixels, 50))
        lung = ((heavy < thresh) & (body > 0)).astype(np.uint8) * 255

        k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        lung = cv2.morphologyEx(lung, cv2.MORPH_CLOSE, k5)
        lung = cv2.morphologyEx(lung, cv2.MORPH_OPEN, k5)

        h, w = lung.shape
        half = w // 2
        result = np.zeros((h, w), dtype=bool)
        for x0, x1 in ((0, half), (half, w)):
            side = np.zeros_like(lung)
            side[:, x0:x1] = lung[:, x0:x1]
            n2, labels2, stats2, _ = cv2.connectedComponentsWithStats(side, connectivity=8)
            if n2 < 2:
                continue
            best2 = max(range(1, n2), key=lambda i: stats2[i, cv2.CC_STAT_AREA])
            result |= (labels2 == best2)

        if result.sum() < 0.03 * gray.size:
            print("[Attribution] OpenCV mask heuristic failed, using full frame")
            result[:] = True
        return result

    def _generate_shap(self, image: Image.Image, case_id: str, target_class: int = 0) -> tuple[str, list[dict]] | None:
        try:
            from captum.attr import IntegratedGradients
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            from matplotlib.colors import Normalize

            model = self._get_active_model()
            if model is None:
                print("[Attribution] No model available, skipping")
                return None

            input_tensor, img_array = self._preprocess(image)

            with torch.no_grad():
                output = model(input_tensor)
                pred_class = output.argmax(dim=1).item()
                class_list = config.MODEL_CLASSES
                pred_label = class_list[pred_class] if pred_class < len(class_list) else f"Class {pred_class}"
                pred_conf = torch.softmax(output, dim=1)[0][pred_class].item()

            input_for_ig, _ = self._preprocess(image, ATTR_SIZE)

            ig = IntegratedGradients(model)
            baseline = torch.zeros_like(input_for_ig)
            t_ig = time.time()
            attributions = ig.attribute(input_for_ig, baselines=baseline, target=pred_class, n_steps=25)
            print(f"[Attribution] IntegratedGradients took {time.time()-t_ig:.1f}s (n_steps=25, size={ATTR_SIZE[0]})")

            sv = attributions.detach().numpy()[0]
            sv_2d = np.mean(sv, axis=0)

            sv_2d = cv2.GaussianBlur(sv_2d, (11, 11), 3)

            v_max = np.percentile(np.abs(sv_2d), 99)
            if v_max < 1e-10:
                v_max = np.abs(sv_2d).max()
            sv_clipped = np.clip(sv_2d, -v_max, v_max)

            # Upscale to display resolution so the heatmap overlays the X-ray exactly
            sv_clipped = cv2.resize(sv_clipped, config.MODEL_INPUT_SIZE, interpolation=cv2.INTER_LINEAR)

            input_size = config.MODEL_INPUT_SIZE
            img_384 = cv2.resize(np.array(image.convert("RGB")), input_size)
            lung_mask = self._build_lung_mask(img_384)
            if img_384.ndim == 3:
                img_display = cv2.cvtColor(img_384, cv2.COLOR_RGB2GRAY)
            else:
                img_display = img_384

            sv_norm = sv_clipped / (v_max + 1e-10)
            # Boost weak attributions with power curve (sqrt) for visible heatmap
            sv_boosted = np.sign(sv_norm) * np.power(np.abs(sv_norm), 0.4)
            colormap_input = (sv_boosted + 1) / 2
            cmap = matplotlib.colormaps['RdBu_r']
            rgba = cmap(colormap_input)
            alpha = np.clip(np.abs(sv_boosted) * 0.9, 0, 0.9)
            alpha *= lung_mask
            rgba[:, :, 3] = alpha

            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            ax.imshow(img_display, cmap='gray', vmin=0, vmax=255)
            ax.imshow(rgba)
            ax.set_title(f'Pixel Attribution\nPredicted: {pred_label}', fontsize=13, fontweight='bold')
            ax.axis('off')

            sm = cm.ScalarMappable(cmap=cmap, norm=Normalize(-v_max, v_max))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Attribution Value', fontsize=11)

            legend_text = "Red = Positive contribution\nBlue = Negative contribution\nGray = Neutral"
            ax.text(0.02, -0.02, legend_text, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            output_path = os.path.join(config.OUTPUT_DIR, f"{case_id}_shap.png")
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"[Attribution] Saved to {output_path} (class={pred_label}, conf={pred_conf:.1%}, IntegratedGradients)")
            return output_path, self._regional_importance(sv_clipped, lung_mask)

        except ImportError:
            print("[Attribution] captum not installed, skipping")
            return None
        except Exception as e:
            print(f"[Attribution] Error: {e}")
            return None

    def _regional_importance(self, attribution: np.ndarray, mask: np.ndarray | None = None) -> list[dict]:
        """Aggregate pixel attribution into six lung-zone importance scores (percent).

        When a lung mask is provided, only attribution inside the masked lung
        pixels contributes to each zone's score.
        """
        h, w = attribution.shape
        bands = ["Upper", "Middle", "Lower"]
        sides = ["Left", "Right"]
        zones = []
        for band_i, band_name in enumerate(bands):
            y0, y1 = int(h * band_i / 3), int(h * (band_i + 1) / 3)
            for side_i, side_name in enumerate(sides):
                x0, x1 = int(w * side_i / 2), int(w * (side_i + 1) / 2)
                zone_abs = np.abs(attribution[y0:y1, x0:x1])
                if mask is not None:
                    zone_mask = mask[y0:y1, x0:x1]
                    mean = float(zone_abs[zone_mask].mean()) if zone_mask.any() else 0.0
                else:
                    mean = float(zone_abs.mean())
                zones.append({
                    "feature": f"{band_name} {side_name} Lung",
                    "importance": mean,
                })
        total = sum(z["importance"] for z in zones)
        if total > 0:
            for z in zones:
                z["importance"] = round(z["importance"] / total * 100, 1)
        return zones
