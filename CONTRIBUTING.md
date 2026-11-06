# Contributing to ADEWI-Rwanda

Thank you for your interest in contributing to the ADEWI-Rwanda research project.

## Repository layout

```text
adewi-rwanda/
├── src/adewi/          # Core Python package (indices, anomalies, lead time, etc.)
├── app/                # Interactive Streamlit Explorer (streamlit_app.py)
├── config/             # Configuration file (config.yaml)
├── data/
│   ├── raw/            # Raw time series & placeholder crop data
│   └── processed/      # Standardized indices & processed time series
├── notebooks/          # Step-by-step exploratory Jupyter notebooks (01–05)
├── paper/              # Academic manuscript template (manuscript_template.md)
├── results/
│   ├── figures/        # Publication-ready charts & maps (300 DPI PNG)
│   ├── tables/         # Summary CSVs & multi-sheet Excel workbooks
│   └── run_report.json # Machine-readable execution report
├── scripts/            # Standalone analysis & GEE export scripts
│   ├── sensitivity_analysis.py    # Multi-scenario weight sensitivity analysis
│   ├── gee_export_timeseries.py   # Python Earth Engine export script
│   ├── gee_export_code_editor.js  # JavaScript Earth Engine Code Editor script
│   └── deafrica_sandbox_extract.py# Digital Earth Africa extraction template
└── tests/              # Pytest unit & integration test suite
```

## Setting up a development environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e ".[dev]"   # installs package in editable mode with test dependencies
```

### Linux / macOS (Bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Running the tests & coverage

```powershell
# Run all tests
pytest tests/ -v

# Run tests with code coverage report
pytest --cov=adewi tests/
```

All tests in `tests/` must pass before submitting changes. Tests rely solely on synthetic and fixture data — no external cloud or GEE credentials are required.

## Coding conventions

- **Python version:** Python ≥ 3.10.
- **Type hints:** Required on all public functions and module boundaries.
- **Docstrings:** NumPy-style docstrings documenting parameters, return values, and exceptions.
- **Path handling:** Never hardcode absolute paths; always resolve paths using `adewi.config.load_config()` and `Path` objects.
- **Reproducibility:** Fix random seeds when generating simulated data or stochastic models.

## Scripts & Utilities

- `scripts/sensitivity_analysis.py`: Evaluates lead times under alternative weighting regimes (e.g., rainfall-dominant, equal-weights, leave-one-out). Run with:
  ```powershell
  python scripts/sensitivity_analysis.py
  ```
- `scripts/gee_export_code_editor.js`: Copy and paste into the [Google Earth Engine Code Editor](https://code.earthengine.google.com/) to export real observational data for Eastern and Southern Rwanda.
- `scripts/gee_export_timeseries.py`: Python Earth Engine automated export script.

## Changing index weights or thresholds

Modify `config/config.yaml` under `weights:` or `drought:`. Execute `adewi` or `python -m adewi` to recompute results. Document any changes in `CHANGELOG.md` under `[Unreleased]`.

## Academic integrity & data provenance

- **Distinguish synthetic from observational data:** Never cite or report synthetic demonstration outputs as real-world findings.
- **Raw data provenance:** If replacing placeholder data with official NISR or MINAGRI agricultural statistics, document the exact source, citation, and survey version.
- **Output tracking:** Generated figures in `results/figures/` and tables in `results/tables/` are git-ignored to prevent storing generated binary artifacts.

## Reporting issues

Open an issue detailing:
1. The command executed (or steps in the Streamlit app).
2. The full Python traceback / error message.
3. System details (`python --version`, OS).
