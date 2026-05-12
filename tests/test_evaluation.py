"""Tests for evaluation helpers and target-color filtering."""

from cs423_segmentation.evaluation import infer_profile_target_color


def test_infer_profile_target_color_parses_standard_names() -> None:
    assert infer_profile_target_color("rgb_red") == "red"
    assert infer_profile_target_color("hsv_blue") == "blue"
    assert infer_profile_target_color("hsv_yellow") == "yellow"


def test_infer_profile_target_color_strips_tuning_suffix() -> None:
    assert infer_profile_target_color("hsv_red-base") == "red"
    assert infer_profile_target_color("rgb_green-strict") == "green"


def test_infer_profile_target_color_unknown_returns_none() -> None:
    assert infer_profile_target_color("segment_everything") is None
    assert infer_profile_target_color("") is None
