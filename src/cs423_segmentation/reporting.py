"""Report generation helpers for experiment summaries and artifacts."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Optional, Union

from cs423_segmentation.dataset import load_dataset_metadata, load_profile_set
from cs423_segmentation.evaluation import evaluate_dataset, run_experiments
from cs423_segmentation.io_utils import load_image, save_csv, save_text
from cs423_segmentation.pipeline import run_pipeline
from cs423_segmentation.visualization import save_mask_image, save_overlay_image


def generate_report(
    metadata_path: Union[str, Path],
    output_dir: Union[str, Path],
    profile_names: Optional[list[str]] = None,
) -> dict[str, Any]:
    metadata_file = Path(metadata_path).resolve()
    profile_set = load_profile_set(metadata_file)
    selected_profiles = profile_names or sorted(profile_set["profiles"])
    report_root = Path(output_dir)
    report_root.mkdir(parents=True, exist_ok=True)

    tables_dir = report_root / "tables"
    figures_dir = report_root / "figures"
    details_dir = report_root / "details"
    masks_dir = report_root / "visuals" / "masks"
    overlays_dir = report_root / "visuals" / "overlays"
    for directory in (tables_dir, figures_dir, details_dir, masks_dir, overlays_dir):
        directory.mkdir(parents=True, exist_ok=True)

    experiment_summary = run_experiments(
        metadata_file, details_dir / "experiment-summary.json", selected_profiles
    )
    detail_summaries = [
        evaluate_dataset(metadata_file, profile_name, details_dir / f"{profile_name}-detail.json")
        for profile_name in selected_profiles
    ]

    save_csv(
        tables_dir / "profile-summary.csv",
        [
            "profile",
            "exact_match_accuracy",
            "mean_absolute_error",
            "total_false_positives",
            "total_false_negatives",
            "average_runtime_ms",
            "total_runtime_ms",
        ],
        experiment_summary["profiles"],
    )
    save_text(
        tables_dir / "profile-summary.md",
        build_markdown_table(
            experiment_summary["profiles"],
            [
                "profile",
                "exact_match_accuracy",
                "mean_absolute_error",
                "total_false_positives",
                "total_false_negatives",
                "average_runtime_ms",
            ],
            {
                "profile": "Profile",
                "exact_match_accuracy": "Accuracy",
                "mean_absolute_error": "MAE",
                "total_false_positives": "Total FP",
                "total_false_negatives": "Total FN",
                "average_runtime_ms": "Avg Runtime (ms)",
            },
        ),
    )

    # ── Runtime summary table ────────────────────────────────────────────────
    save_csv(
        tables_dir / "runtime-summary.csv",
        ["profile", "average_runtime_ms", "total_runtime_ms"],
        experiment_summary["profiles"],
    )
    save_text(
        tables_dir / "runtime-summary.md",
        build_markdown_table(
            experiment_summary["profiles"],
            ["profile", "average_runtime_ms", "total_runtime_ms"],
            {
                "profile": "Profile",
                "average_runtime_ms": "Avg Runtime per Image (ms)",
                "total_runtime_ms": "Total Runtime (ms)",
            },
        ),
    )

    # ── False-positive / False-negative summary table ────────────────────────
    save_csv(
        tables_dir / "fp-fn-summary.csv",
        ["profile", "exact_match_accuracy", "total_false_positives", "total_false_negatives"],
        experiment_summary["profiles"],
    )
    save_text(
        tables_dir / "fp-fn-summary.md",
        build_markdown_table(
            experiment_summary["profiles"],
            [
                "profile",
                "exact_match_accuracy",
                "total_false_positives",
                "total_false_negatives",
            ],
            {
                "profile": "Profile",
                "exact_match_accuracy": "Accuracy",
                "total_false_positives": "False Positives (total)",
                "total_false_negatives": "False Negatives (total)",
            },
        ),
    )

    condition_rows = build_condition_summary_rows(detail_summaries)
    save_csv(
        tables_dir / "condition-summary.csv",
        [
            "profile",
            "condition_type",
            "condition_value",
            "image_count",
            "exact_match_accuracy",
            "mean_absolute_error",
        ],
        condition_rows,
    )
    save_text(
        tables_dir / "condition-summary.md",
        build_markdown_table(
            condition_rows,
            [
                "profile",
                "condition_type",
                "condition_value",
                "image_count",
                "exact_match_accuracy",
                "mean_absolute_error",
            ],
            {
                "profile": "Profile",
                "condition_type": "Condition Type",
                "condition_value": "Condition Value",
                "image_count": "Image Count",
                "exact_match_accuracy": "Exact Match Accuracy",
                "mean_absolute_error": "Mean Absolute Error",
            },
        ),
    )

    error_rows = build_error_rows(detail_summaries)
    worst_case_rows = build_worst_case_rows(detail_summaries)
    error_type_rows = build_error_type_rows(detail_summaries)

    save_csv(
        tables_dir / "error-analysis.csv",
        [
            "profile",
            "image_id",
            "image_path",
            "target_color",
            "expected_count",
            "predicted_count",
            "absolute_error",
            "false_positives",
            "false_negatives",
            "lighting",
            "background",
            "overlap",
        ],
        error_rows,
    )
    save_text(
        tables_dir / "error-analysis.md",
        build_markdown_table(
            error_rows,
            [
                "profile",
                "image_id",
                "target_color",
                "expected_count",
                "predicted_count",
                "absolute_error",
                "false_positives",
                "false_negatives",
            ],
            {
                "profile": "Profile",
                "image_id": "Image ID",
                "target_color": "Color",
                "expected_count": "Expected",
                "predicted_count": "Predicted",
                "absolute_error": "Abs Error",
                "false_positives": "FP",
                "false_negatives": "FN",
            },
        ),
    )

    save_csv(
        tables_dir / "worst-cases.csv",
        [
            "profile",
            "image_id",
            "absolute_error",
            "false_positives",
            "false_negatives",
            "lighting",
            "background",
            "overlap",
        ],
        worst_case_rows,
    )
    save_text(
        tables_dir / "worst-cases.md",
        build_markdown_table(
            worst_case_rows,
            [
                "profile",
                "image_id",
                "absolute_error",
                "false_positives",
                "false_negatives",
                "lighting",
                "background",
                "overlap",
            ],
            {
                "profile": "Profile",
                "image_id": "Image ID",
                "absolute_error": "Abs Error",
                "false_positives": "FP",
                "false_negatives": "FN",
                "lighting": "Lighting",
                "background": "Background",
                "overlap": "Overlap",
            },
        ),
    )

    save_csv(
        tables_dir / "error-type-summary.csv",
        ["profile", "error_type", "image_count", "rate"],
        error_type_rows,
    )
    save_text(
        tables_dir / "error-type-summary.md",
        build_markdown_table(
            error_type_rows,
            ["profile", "error_type", "image_count", "rate"],
            {
                "profile": "Profile",
                "error_type": "Error Type",
                "image_count": "Image Count",
                "rate": "Rate",
            },
        ),
    )

    _write_visualizations(
        metadata_file,
        profile_set["profiles"],
        selected_profiles,
        masks_dir,
        overlays_dir,
    )
    _write_figure_exports(experiment_summary["profiles"], condition_rows, figures_dir)
    return {
        "experiment_summary": experiment_summary,
        "condition_rows": condition_rows,
        "error_rows": error_rows,
        "worst_case_rows": worst_case_rows,
        "error_type_rows": error_type_rows,
        "tables_dir": str(tables_dir),
        "figures_dir": str(figures_dir),
        "details_dir": str(details_dir),
        "output_dir": str(report_root),
    }


def build_report_bundle(
    metadata_path: Union[str, Path], output_dir: Union[str, Path], include_tuning: bool = True
) -> dict[str, Any]:
    metadata_file = Path(metadata_path).resolve()
    validation = validate_dataset_or_raise(metadata_file)
    report = generate_report(metadata_file, output_dir)
    tuning_outputs = []
    if include_tuning:
        from cs423_segmentation.tuning import tune_profile

        profile_set = load_profile_set(metadata_file)
        tuning_root = Path(output_dir) / "tuning"
        tuning_root.mkdir(parents=True, exist_ok=True)
        for profile_name in sorted(profile_set["profiles"]):
            tuning_outputs.append(
                tune_profile(metadata_file, profile_name, tuning_root / profile_name)
            )
    bundle_summary = {
        "validation": validation,
        "report": report,
        "tuning": tuning_outputs,
    }
    save_text(
        Path(output_dir) / "README.md",
        _build_bundle_readme(report, include_tuning=include_tuning),
    )
    return bundle_summary


def build_condition_summary_rows(detail_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in detail_summaries:
        for condition_type in ("lighting", "background", "overlap"):
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for item in summary["per_image"]:
                grouped[item[condition_type]].append(item)

            for condition_value, items in sorted(grouped.items()):
                exact_matches = sum(int(item["absolute_error"] == 0) for item in items)
                mean_absolute_error = sum(item["absolute_error"] for item in items) / len(items)
                rows.append(
                    {
                        "profile": summary["profile"],
                        "condition_type": condition_type,
                        "condition_value": condition_value,
                        "image_count": len(items),
                        "exact_match_accuracy": exact_matches / len(items),
                        "mean_absolute_error": mean_absolute_error,
                    }
                )
    return rows


def build_markdown_table(
    rows: list[dict[str, Any]], fieldnames: list[str], labels: dict[str, str]
) -> str:
    header = "| " + " | ".join(labels[field] for field in fieldnames) + " |"
    divider = (
        "| "
        + " | ".join("---:" if field != fieldnames[0] else "---" for field in fieldnames)
        + " |"
    )
    body = []
    for row in rows:
        body.append(
            "| " + " | ".join(_format_markdown_value(row[field]) for field in fieldnames) + " |"
        )
    return "\n".join([header, divider, *body]) + "\n"


def build_error_rows(detail_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in detail_summaries:
        for item in summary["per_image"]:
            if item["absolute_error"] == 0:
                continue
            rows.append({"profile": summary["profile"], **item})
    rows.sort(
        key=lambda row: (
            row["profile"],
            -row["absolute_error"],
            -row["false_negatives"],
            -row["false_positives"],
            row["image_id"],
        )
    )
    return rows


def build_worst_case_rows(
    detail_summaries: list[dict[str, Any]], limit_per_profile: int = 3
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    error_rows = build_error_rows(detail_summaries)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in error_rows:
        grouped[row["profile"]].append(row)

    for _profile, items in sorted(grouped.items()):
        rows.extend(items[:limit_per_profile])
    return rows


def build_error_type_rows(detail_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in detail_summaries:
        total_images = len(summary["per_image"])
        exact = 0
        overcount = 0
        undercount = 0
        mixed = 0
        for item in summary["per_image"]:
            if item["absolute_error"] == 0:
                exact += 1
            elif item["false_positives"] > 0 and item["false_negatives"] > 0:
                mixed += 1
            elif item["false_positives"] > 0:
                overcount += 1
            else:
                undercount += 1

        for error_type, image_count in (
            ("exact", exact),
            ("overcount", overcount),
            ("undercount", undercount),
            ("mixed", mixed),
        ):
            rows.append(
                {
                    "profile": summary["profile"],
                    "error_type": error_type,
                    "image_count": image_count,
                    "rate": image_count / total_images if total_images else 0.0,
                }
            )
    return rows


def _format_markdown_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _write_visualizations(
    metadata_path: Path,
    profiles: dict[str, dict[str, Any]],
    selected_profiles: list[str],
    masks_dir: Path,
    overlays_dir: Path,
) -> None:
    metadata = load_dataset_metadata(metadata_path)
    dataset_root = metadata_path.parents[3]

    for item in metadata["images"]:
        image = load_image(dataset_root / item["image_path"])
        for profile_name in selected_profiles:
            result = run_pipeline(image, profiles[profile_name])
            base_name = f"{item['image_id']}-{profile_name}"
            save_mask_image(result.mask, masks_dir / f"{base_name}.png")
            save_overlay_image(image, result.mask, overlays_dir / f"{base_name}.png")


def _write_figure_exports(
    profile_rows: list[dict[str, Any]], condition_rows: list[dict[str, Any]], figures_dir: Path
) -> None:
    save_text(figures_dir / "profile-accuracy.svg", _build_profile_accuracy_svg(profile_rows))
    save_text(figures_dir / "profile-runtime.svg", _build_profile_runtime_svg(profile_rows))
    save_text(
        figures_dir / "lighting-accuracy.svg", _build_condition_svg(condition_rows, "lighting")
    )


def _build_profile_accuracy_svg(profile_rows: list[dict[str, Any]]) -> str:
    return _build_bar_chart_svg(
        title="Profile Accuracy",
        items=[(row["profile"], row["exact_match_accuracy"]) for row in profile_rows],
        max_value=1.0,
    )


def _build_profile_runtime_svg(profile_rows: list[dict[str, Any]]) -> str:
    max_runtime = max((row["average_runtime_ms"] for row in profile_rows), default=1.0)
    return _build_bar_chart_svg(
        title="Profile Runtime (ms)",
        items=[(row["profile"], row["average_runtime_ms"]) for row in profile_rows],
        max_value=max_runtime or 1.0,
    )


def _build_condition_svg(condition_rows: list[dict[str, Any]], condition_type: str) -> str:
    filtered = [
        (f"{row['profile']}:{row['condition_value']}", row["exact_match_accuracy"])
        for row in condition_rows
        if row["condition_type"] == condition_type
    ]
    return _build_bar_chart_svg(
        title=f"{condition_type.title()} Accuracy",
        items=filtered,
        max_value=1.0,
    )


def _build_bar_chart_svg(title: str, items: list[tuple[str, float]], max_value: float) -> str:
    width = 720
    row_height = 36
    chart_left = 180
    chart_width = 460
    height = 80 + max(len(items), 1) * row_height
    safe_max = max(max_value, 1e-6)
    bars = []
    for index, (label, value) in enumerate(items):
        y = 50 + index * row_height
        bar_width = int((value / safe_max) * chart_width)
        bars.append(
            f'<text x="20" y="{y + 18}" font-size="14">{label}</text>'
            f'<rect x="{chart_left}" y="{y}" width="{bar_width}" height="20" fill="#2f6fed" />'
            f'<text x="{chart_left + bar_width + 8}" y="{y + 16}" font-size="13">{value:.4f}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect width="100%" height="100%" fill="white" />'
        f'<text x="20" y="28" font-size="20" font-weight="bold">{title}</text>'
        + "".join(bars)
        + "</svg>"
    )


def validate_dataset_or_raise(metadata_path: Path) -> dict[str, Any]:
    from cs423_segmentation.dataset import validate_dataset

    result = validate_dataset(metadata_path)
    if result["is_valid"]:
        return result
    raise ValueError("Dataset validation failed: " + "; ".join(result["errors"]))


def _build_bundle_readme(report: dict[str, Any], include_tuning: bool) -> str:
    lines = [
        "# Report Bundle",
        "",
        "Generated artifacts:",
        "",
        "- `tables/`: CSV and Markdown summaries",
        "- `figures/`: SVG figure exports for report/presentation reuse",
        "- `details/`: raw JSON summaries for each profile",
        "- `visuals/masks/`: binary mask images",
        "- `visuals/overlays/`: overlay previews",
    ]
    if include_tuning:
        lines.append("- `tuning/`: candidate threshold rankings per profile")
    lines.extend(["", f"Profiles in bundle: {len(report['experiment_summary']['profiles'])}"])
    return "\n".join(lines) + "\n"
