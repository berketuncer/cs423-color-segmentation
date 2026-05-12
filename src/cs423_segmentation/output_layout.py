"""Stable, human-readable subfolder names under a report or bundle root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportLayout:
    """Directory layout for `generate_report` / `build-bundle` output."""

    root: Path

    @property
    def tables(self) -> Path:
        """Spreadsheet-friendly summaries (CSV + Markdown)."""
        return self.root / "tables"

    @property
    def charts(self) -> Path:
        """Simple SVG bar charts for slides or reports."""
        return self.root / "charts"

    @property
    def json_details(self) -> Path:
        """Machine-readable per-profile summaries and experiment JSON."""
        return self.root / "json-details"

    @property
    def masks(self) -> Path:
        """Binary mask PNGs (segmentation result per image and profile)."""
        return self.root / "image-previews" / "masks"

    @property
    def overlays(self) -> Path:
        """Overlay PNGs (original image + mask highlight)."""
        return self.root / "image-previews" / "overlays"

    @property
    def threshold_tuning(self) -> Path:
        """Ranked threshold / profile variants from `tune-profile`."""
        return self.root / "threshold-tuning"

    def mkdirs_for_report(self) -> None:
        for path in (self.tables, self.charts, self.json_details, self.masks, self.overlays):
            path.mkdir(parents=True, exist_ok=True)
