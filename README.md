# CS423 Color Segmentation Project

Classical computer vision pipeline for color-based object extraction and counting.

Current baseline implementation includes:

- RGB thresholding
- HSV thresholding
- binary morphology cleanup
- connected-component counting
- dataset evaluation CLI
- versioned profile configuration
- bundled sample dataset for reproducible smoke tests
- real-dataset folder/template for final project data collection

## Mandatory Dataset Checklist

These are now mandatory project requirements, not optional nice-to-haves:

- fixed metadata schema for every image
- `expected_count` for every image
- `lighting`, `background`, and `overlap` labels for every image
- versioned profile configuration files kept separate from dataset metadata

## Setup

```bash
make install-dev
```

## Validation

```bash
make validate-pr
```

This runs:

- format checks
- lint
- tests
- smoke test

## Sample Evaluation

```bash
make evaluate-rgb
make evaluate-hsv
make run-experiments
make generate-report
make tune-sample-rgb
make tune-sample-hsv
make build-sample-bundle
```

Outputs are written under `results/datasets/...` (see `results/README.md` for a Turkish layout guide).

For profiles named `rgb_<color>` or `hsv_<color>` (including tuning variants like `hsv_red-base`), evaluation uses **only images whose metadata `target_color` matches** that color, so a red profile is not scored on blue-target photos.

`make generate-report` writes (under `results/datasets/sample/full-report/`):

- `tables/profile-summary.csv`
- `tables/condition-summary.csv`
- `charts/profile-accuracy.svg`
- `json-details/experiment-summary.json`
- `image-previews/masks/*.png`
- `image-previews/overlays/*.png`

`make tune-sample-rgb` and `make tune-sample-hsv` write ranked tuning artifacts under:

- `results/datasets/sample/threshold-tuning/<profile>/tuning-results.json`
- `results/datasets/sample/threshold-tuning/<profile>/tuning-results.csv`
- `results/datasets/sample/threshold-tuning/<profile>/tuning-results.md`

`make build-sample-bundle` writes a structured final-material bundle under:

- `results/datasets/sample/presentation-bundle/tables/`
- `results/datasets/sample/presentation-bundle/charts/`
- `results/datasets/sample/presentation-bundle/json-details/`
- `results/datasets/sample/presentation-bundle/image-previews/`
- `results/datasets/sample/presentation-bundle/threshold-tuning/`

When the real dataset is ready, run:

```bash
make build-real-bundle
```

## Real Dataset Preparation

Use the real dataset template and guide:

- metadata template: `data/real/metadata/dataset.template.json`
- starter profiles: `configs/profiles/v1/multi-color-template.json`
- collection guide: `docs/dataset-collection-guide.md`

After your team fills `data/real/metadata/dataset.json`, run:

```bash
make validate-real-dataset
```

## CLI Usage

```bash
PYTHONPATH=src python3 -m cs423_segmentation evaluate \
  --metadata data/sample/metadata/dataset.json \
  --profile hsv_red \
  --output results/datasets/sample/quick-eval/hsv_red.json

PYTHONPATH=src python3 -m cs423_segmentation run-experiments \
  --metadata data/sample/metadata/dataset.json \
  --output results/datasets/sample/quick-eval/experiment-summary.json
```

## Repository Rules

Read before contributing:

- `CONTRIBUTING.md`
- `AGENTS.md`
- `docs/ai-tooling.md`
