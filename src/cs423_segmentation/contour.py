"""Contour extraction from binary masks using boundary tracing.

This module provides a classical contour-finding approach as an alternative
(or complement) to Connected Component Labeling for object counting.
A contour is the ordered list of boundary pixels surrounding a connected
white region in a binary mask.
"""

from __future__ import annotations

import numpy as np


def extract_contours(mask: np.ndarray, min_area: int = 1) -> list[np.ndarray]:
    """Extract contours (boundary pixel sets) from a binary mask.

    For each connected white region in *mask* whose area is >= *min_area*,
    the function returns a boolean array of the same shape as *mask* where
    only the boundary pixels of that region are True.

    Args:
        mask: 2-D boolean array (white pixels = foreground objects).
        min_area: Minimum number of *interior* pixels for a region to be
            included.  Regions smaller than this are discarded as noise.

    Returns:
        A list of 2-D boolean arrays, one per detected contour.
    """
    if mask.ndim != 2:
        raise ValueError("extract_contours expects a 2-D mask array.")

    # Erode the mask by one pixel to get the interior.
    # Boundary = mask XOR interior.
    interior = _erode_once(mask)
    boundary_mask = mask & ~interior

    # Label connected regions in the *original* mask (interior + boundary)
    # so each contour corresponds to exactly one object.
    from cs423_segmentation.counting import extract_components

    components = extract_components(mask, min_component_size=min_area)
    contours: list[np.ndarray] = []
    for component in components:
        contour = component & boundary_mask
        if contour.any():
            contours.append(contour)
    return contours


def count_contours(mask: np.ndarray, min_area: int = 1) -> tuple[int, list[int]]:
    """Count objects in *mask* via contour extraction.

    Args:
        mask: 2-D boolean mask.
        min_area: Minimum region area to count.

    Returns:
        A tuple ``(count, contour_lengths)`` where *count* is the number of
        detected objects and *contour_lengths* is the perimeter (number of
        boundary pixels) of each contour.
    """
    contours = extract_contours(mask, min_area=min_area)
    lengths = [int(c.sum()) for c in contours]
    return len(contours), lengths


def _erode_once(mask: np.ndarray) -> np.ndarray:
    """Remove the outermost layer of pixels from every foreground region.

    Equivalent to a single binary erosion with a 4-connected structuring
    element (cross kernel), implemented with pure NumPy shifts so that the
    module remains dependency-free.
    """
    m = mask.astype(bool)
    # A pixel survives erosion only when ALL four 4-connected neighbours
    # are also foreground.
    eroded = (
        m
        & np.roll(m, 1, axis=0)   # pixel above
        & np.roll(m, -1, axis=0)  # pixel below
        & np.roll(m, 1, axis=1)   # pixel to the left
        & np.roll(m, -1, axis=1)  # pixel to the right
    )
    # np.roll wraps around at borders; pixels on the image border should
    # never survive erosion (they lack at least one true neighbour).
    eroded[0, :] = False
    eroded[-1, :] = False
    eroded[:, 0] = False
    eroded[:, -1] = False
    return eroded
