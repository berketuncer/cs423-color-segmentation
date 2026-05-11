"""Core segmentation pipelines for RGB and HSV thresholding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from cs423_segmentation.color import threshold_hsv, threshold_rgb
from cs423_segmentation.contour import count_contours
from cs423_segmentation.counting import count_connected_components, extract_components
from cs423_segmentation.morphology import closing, opening


@dataclass
class PipelineResult:
    count: int
    component_sizes: list[int]
    mask: np.ndarray
    # Contour-based count (boundary tracing), kept for comparison with CCL.
    contour_count: int = 0
    contour_lengths: list[int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.contour_lengths is None:
            self.contour_lengths = []


def run_pipeline(image: np.ndarray, config: dict[str, Any]) -> PipelineResult:
    color_space = config["color_space"].lower()
    morphology_config = config.get("morphology", {})
    min_component_size = int(config.get("min_component_size", 1))

    if color_space == "rgb":
        mask = threshold_rgb(image, config["lower"], config["upper"])
    elif color_space == "hsv":
        mask = threshold_hsv(image, config["ranges"])
    else:
        raise ValueError(f"Unsupported color space: {color_space}")

    opened = opening(
        mask,
        kernel_size=int(morphology_config.get("kernel_size", 3)),
        iterations=int(morphology_config.get("opening_iterations", 1)),
    )
    cleaned = closing(
        opened,
        kernel_size=int(morphology_config.get("kernel_size", 3)),
        iterations=int(morphology_config.get("closing_iterations", 1)),
    )
    cleaned = _apply_refinement(image, cleaned, config.get("refinement"))

    count, component_sizes = count_connected_components(
        cleaned, min_component_size=min_component_size
    )
    contour_count, contour_lengths = count_contours(cleaned, min_area=min_component_size)
    return PipelineResult(
        count=count,
        component_sizes=component_sizes,
        mask=cleaned,
        contour_count=contour_count,
        contour_lengths=contour_lengths,
    )


def _apply_refinement(
    image: np.ndarray, mask: np.ndarray, refinement_config: Optional[dict[str, Any]]
) -> np.ndarray:
    if not refinement_config:
        return mask
    if refinement_config["type"] != "edge_supported":
        raise ValueError(f"Unsupported refinement type: {refinement_config['type']}")

    gradient_threshold = float(refinement_config.get("gradient_threshold", 40))
    min_edge_fraction = float(refinement_config.get("min_edge_fraction", 0.2))
    grayscale = image.astype(np.float32).mean(axis=-1)

    refined = np.zeros(mask.shape, dtype=bool)
    for component in extract_components(mask, min_component_size=1):
        edge_fraction = _component_internal_edge_fraction(grayscale, component, gradient_threshold)
        if edge_fraction >= min_edge_fraction:
            refined |= component
    return refined


def _component_internal_edge_fraction(
    grayscale: np.ndarray, component: np.ndarray, threshold: float
) -> float:
    component_size = int(component.sum())
    if component_size == 0:
        return 0.0

    rows, cols = np.nonzero(component)
    row_start, row_end = int(rows.min()), int(rows.max()) + 1
    col_start, col_end = int(cols.min()), int(cols.max()) + 1
    component_crop = component[row_start:row_end, col_start:col_end]
    grayscale_crop = grayscale[row_start:row_end, col_start:col_end]

    supported_pixels = np.zeros(component_crop.shape, dtype=bool)

    vertical_pairs = component_crop[:-1, :] & component_crop[1:, :]
    vertical_support = vertical_pairs & (
        np.abs(grayscale_crop[:-1, :] - grayscale_crop[1:, :]) >= threshold
    )
    supported_pixels[:-1, :] |= vertical_support
    supported_pixels[1:, :] |= vertical_support

    horizontal_pairs = component_crop[:, :-1] & component_crop[:, 1:]
    horizontal_support = horizontal_pairs & (
        np.abs(grayscale_crop[:, :-1] - grayscale_crop[:, 1:]) >= threshold
    )
    supported_pixels[:, :-1] |= horizontal_support
    supported_pixels[:, 1:] |= horizontal_support

    return float(np.logical_and(supported_pixels, component_crop).sum()) / component_size
