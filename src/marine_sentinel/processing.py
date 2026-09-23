import cv2
import numpy as np

from marine_sentinel.config import settings


def prepare_sonar(image: np.ndarray) -> np.ndarray:
    """Reduce speckle noise and normalize local contrast in sonar imagery."""
    grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image
    denoised = cv2.fastNlMeansDenoising(grayscale, None, h=settings.sonar_denoise_strength,
                                        templateWindowSize=settings.sonar_denoise_template_window,
                                        searchWindowSize=settings.sonar_denoise_search_window)
    return cv2.createCLAHE(clipLimit=settings.sonar_clahe_clip_limit,
                           tileGridSize=(settings.sonar_clahe_tile_grid, settings.sonar_clahe_tile_grid)).apply(denoised)


def quality_metrics(processed: np.ndarray) -> dict[str, float]:
    """Simple mission-health diagnostics for the operator dashboard."""
    mean, std_dev = cv2.meanStdDev(processed)
    dropout_ratio = float(np.mean(processed < settings.sonar_dropout_pixel_value))
    return {
        "mean_backscatter": round(float(mean[0][0]), 1),
        "texture_contrast": round(float(std_dev[0][0]), 1),
        "dropout_ratio_percent": round(dropout_ratio * 100, 2),
    }
