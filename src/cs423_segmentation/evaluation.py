"""Batch evaluation utilities for dataset-level pipeline comparisons."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional, Union

from cs423_segmentation.dataset import load_dataset_metadata, load_profile_set
from cs423_segmentation.io_utils import load_image, save_json
from cs423_segmentation.pipeline import run_pipeline


def infer_profile_target_color(profile_name: str) -> Optional[str]:
    """Return the object color a profile segments, if the name follows ``rgb_*`` / ``hsv_*``.

    Tuning candidates use names like ``hsv_red-base``; the color is taken from the stem
    before the first ``-``. Unknown patterns return ``None`` (evaluate on every image).
    """

    stem = profile_name.split("-", 1)[0]
    parts = stem.split("_", 1)
    if len(parts) != 2:
        return None
    space, color = parts
    if space not in ("rgb", "hsv") or not color:
        return None
    return color


def evaluate_dataset(
    metadata_path: Union[str, Path], profile_name: str, output_path: Union[str, Path]
) -> dict[str, Any]:
    summary = evaluate_dataset_summary(metadata_path, profile_name)
    save_json(output_path, summary)
    return summary


def evaluate_dataset_summary(
    metadata_path: Union[str, Path],
    profile_name: str,
    profile_override: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    metadata_file = Path(metadata_path).resolve()
    metadata = load_dataset_metadata(metadata_file)
    profile_set = load_profile_set(metadata_file)
    profile = profile_override or profile_set["profiles"][profile_name]
    dataset_root = metadata_file.parents[3]
    color_filter = infer_profile_target_color(profile_name)

    per_image_results: list[dict[str, Any]] = []
    absolute_errors: list[int] = []
    exact_matches = 0
    total_runtime_ms = 0.0

    for item in metadata["images"]:
        if color_filter is not None and item["target_color"] != color_filter:
            continue
        image_path = dataset_root / item["image_path"]
        expected_count = int(item["expected_count"])
        image = load_image(image_path)

        started = time.perf_counter()
        result = run_pipeline(image, profile)
        runtime_ms = (time.perf_counter() - started) * 1000.0

        absolute_error = abs(result.count - expected_count)
        false_positives = max(result.count - expected_count, 0)
        false_negatives = max(expected_count - result.count, 0)

        exact_matches += int(result.count == expected_count)
        absolute_errors.append(absolute_error)
        total_runtime_ms += runtime_ms

        per_image_results.append(
            {
                "image_id": item["image_id"],
                "image_path": item["image_path"],
                "target_color": item["target_color"],
                "expected_count": expected_count,
                "predicted_count": result.count,
                "absolute_error": absolute_error,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "contour_count": result.contour_count,
                "contour_lengths": result.contour_lengths,
                "lighting": item["lighting"],
                "background": item["background"],
                "overlap": item["overlap"],
                "runtime_ms": round(runtime_ms, 4),
                "component_sizes": result.component_sizes,
            }
        )

    image_count = len(per_image_results)
    if image_count == 0:
        return {
            "dataset_name": metadata["dataset_name"],
            "metadata_schema_version": metadata["metadata_schema_version"],
            "profile_set_name": profile_set["profile_set_name"],
            "profile_set_version": profile_set["profile_set_version"],
            "profile": profile_name,
            "target_color_filter": color_filter,
            "image_count": 0,
            "exact_match_accuracy": 0.0,
            "mean_absolute_error": 0.0,
            "total_false_positives": 0,
            "total_false_negatives": 0,
            "average_runtime_ms": 0.0,
            "total_runtime_ms": 0.0,
            "per_image": [],
        }

    total_fp = sum(r["false_positives"] for r in per_image_results)
    total_fn = sum(r["false_negatives"] for r in per_image_results)
    summary = {
        "dataset_name": metadata["dataset_name"],
        "metadata_schema_version": metadata["metadata_schema_version"],
        "profile_set_name": profile_set["profile_set_name"],
        "profile_set_version": profile_set["profile_set_version"],
        "profile": profile_name,
        "target_color_filter": color_filter,
        "image_count": image_count,
        "exact_match_accuracy": exact_matches / image_count if image_count else 0.0,
        "mean_absolute_error": sum(absolute_errors) / image_count if image_count else 0.0,
        "total_false_positives": total_fp,
        "total_false_negatives": total_fn,
        "average_runtime_ms": total_runtime_ms / image_count if image_count else 0.0,
        "total_runtime_ms": round(total_runtime_ms, 4),
        "per_image": per_image_results,
    }
    return summary


def run_experiments(
    metadata_path: Union[str, Path],
    output_path: Union[str, Path],
    profile_names: Optional[list[str]] = None,
) -> dict[str, Any]:
    metadata_file = Path(metadata_path).resolve()
    metadata = load_dataset_metadata(metadata_file)
    profile_set = load_profile_set(metadata_file)
    selected_profiles = profile_names or sorted(profile_set["profiles"])

    summaries = []
    for profile_name in selected_profiles:
        summary = evaluate_dataset(
            metadata_file, profile_name, Path(output_path).with_name(f"{profile_name}-detail.json")
        )
        summaries.append(
            {
                "profile": profile_name,
                "image_count": summary["image_count"],
                "exact_match_accuracy": summary["exact_match_accuracy"],
                "mean_absolute_error": summary["mean_absolute_error"],
                "total_false_positives": summary["total_false_positives"],
                "total_false_negatives": summary["total_false_negatives"],
                "average_runtime_ms": summary["average_runtime_ms"],
                "total_runtime_ms": summary["total_runtime_ms"],
            }
        )

    experiment_summary = {
        "dataset_name": metadata["dataset_name"],
        "metadata_schema_version": metadata["metadata_schema_version"],
        "profile_set_name": profile_set["profile_set_name"],
        "profile_set_version": profile_set["profile_set_version"],
        "profiles": summaries,
    }
    save_json(output_path, experiment_summary)
    return experiment_summary
