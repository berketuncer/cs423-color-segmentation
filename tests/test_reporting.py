import csv
from pathlib import Path

from cs423_segmentation.reporting import (
    build_condition_summary_rows,
    build_error_rows,
    build_error_type_rows,
    build_report_bundle,
    build_worst_case_rows,
    generate_report,
)


def test_build_condition_summary_rows_groups_by_condition() -> None:
    rows = build_condition_summary_rows(
        [
            {
                "profile": "rgb_red",
                "per_image": [
                    {
                        "lighting": "controlled",
                        "background": "plain",
                        "overlap": "none",
                        "absolute_error": 0,
                    },
                    {
                        "lighting": "dim",
                        "background": "plain",
                        "overlap": "none",
                        "absolute_error": 1,
                    },
                ],
            }
        ]
    )
    assert any(
        row["condition_type"] == "lighting" and row["condition_value"] == "controlled"
        for row in rows
    )
    assert any(
        row["condition_type"] == "lighting" and row["condition_value"] == "dim" for row in rows
    )


def test_generate_report_writes_csv_and_visualization_artifacts(tmp_path: Path) -> None:
    report = generate_report("data/sample/metadata/dataset.json", tmp_path)
    profile_summary = tmp_path / "tables" / "profile-summary.csv"
    condition_summary = tmp_path / "tables" / "condition-summary.csv"
    profile_summary_md = tmp_path / "tables" / "profile-summary.md"
    condition_summary_md = tmp_path / "tables" / "condition-summary.md"
    error_analysis = tmp_path / "tables" / "error-analysis.csv"
    worst_cases = tmp_path / "tables" / "worst-cases.csv"
    error_type_summary = tmp_path / "tables" / "error-type-summary.csv"
    figure_svg = tmp_path / "charts" / "profile-accuracy.svg"
    mask_image = tmp_path / "image-previews" / "masks" / "sample-001-hsv_red.png"
    overlay_image = tmp_path / "image-previews" / "overlays" / "sample-001-hsv_red.png"

    assert report["experiment_summary"]["profile_set_version"] == "v1"
    assert profile_summary.exists()
    assert condition_summary.exists()
    assert profile_summary_md.exists()
    assert condition_summary_md.exists()
    assert error_analysis.exists()
    assert worst_cases.exists()
    assert error_type_summary.exists()
    assert figure_svg.exists()
    assert mask_image.exists()
    assert overlay_image.exists()

    with profile_summary.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["profile"] for row in rows] == ["hsv_red", "rgb_red"]


def test_error_analysis_helpers_extract_miscounts_and_types() -> None:
    detail_summaries = [
        {
            "profile": "rgb_red",
            "per_image": [
                {
                    "image_id": "ok-1",
                    "image_path": "a",
                    "target_color": "red",
                    "expected_count": 2,
                    "predicted_count": 2,
                    "absolute_error": 0,
                    "false_positives": 0,
                    "false_negatives": 0,
                    "lighting": "controlled",
                    "background": "plain",
                    "overlap": "none",
                },
                {
                    "image_id": "bad-1",
                    "image_path": "b",
                    "target_color": "red",
                    "expected_count": 2,
                    "predicted_count": 0,
                    "absolute_error": 2,
                    "false_positives": 0,
                    "false_negatives": 2,
                    "lighting": "dim",
                    "background": "plain",
                    "overlap": "none",
                },
            ],
        }
    ]
    error_rows = build_error_rows(detail_summaries)
    worst_rows = build_worst_case_rows(detail_summaries)
    type_rows = build_error_type_rows(detail_summaries)
    assert len(error_rows) == 1
    assert error_rows[0]["image_id"] == "bad-1"
    assert len(worst_rows) == 1
    assert any(row["error_type"] == "undercount" and row["image_count"] == 1 for row in type_rows)


def test_build_report_bundle_writes_structured_output_tree(tmp_path: Path) -> None:
    bundle = build_report_bundle("data/sample/metadata/dataset.json", tmp_path, include_tuning=True)
    assert bundle["validation"]["is_valid"] is True
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "tables" / "profile-summary.csv").exists()
    assert (tmp_path / "charts" / "profile-runtime.svg").exists()
    assert (tmp_path / "json-details" / "experiment-summary.json").exists()
    assert (tmp_path / "image-previews" / "masks" / "sample-001-hsv_red.png").exists()
    assert (tmp_path / "threshold-tuning" / "hsv_red" / "tuning-results.md").exists()


def test_build_report_bundle_skip_tuning_omits_tuning_artifacts(tmp_path: Path) -> None:
    bundle = build_report_bundle(
        "data/sample/metadata/dataset.json", tmp_path, include_tuning=False
    )
    assert bundle["validation"]["is_valid"] is True
    assert (tmp_path / "tables" / "profile-summary.csv").exists()
    assert not (tmp_path / "threshold-tuning").exists()
