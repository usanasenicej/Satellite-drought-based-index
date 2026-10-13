# Contributing to ADEWI-Rwanda

Thank you for your interest in this open research project.

## Repository layout

```
adewi-rwanda/
├── src/adewi/          # Core Python package
├── app/                # Streamlit prototype
├── config/             # config.yaml (weights, thresholds, paths)
├── data/raw/           # Input CSV (GEE or DE Africa export) — not committed
├── data/processed/     # Pipeline outputs — not committed
├── notebooks/          # Jupyter notebooks 01–05
├── paper/              # Manuscript draft (Markdown)
├── results/            # Figures and tables — not committed
├── scripts/            # GEE export scripts
└── tests/              # pytest unit tests
```

## Setting up a development environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"   # installs package + pytest
```

Or with the plain requirements file:

```powershell
pip install -r requirements.txt
pip install pytest
```

## Running the tests

```powershell
pytest tests/ -v
```

All tests in `tests/` must pass on a clean install before submitting a pull
request. Tests use only the synthetic data generator — no GEE credentials are
needed.

## Coding conventions

- Python ≥ 3.10.
- Type hints on all public functions.
- Docstrings in NumPy style.
- One module per logical concern (anomalies, preprocessing, lead time, …).
- No hard-coded paths: always read from `config/config.yaml` via
  `adewi.config.load_config()`.

## Changing index weights

Edit `config/config.yaml` under the `weights:` key. Run
`python -m adewi` to regenerate all outputs. Document the change in
`CHANGELOG.md` under `[Unreleased]`.

## Adding a sensitivity test

Place the test in `scripts/sensitivity_analysis.py` following the pattern of
equal-weight and leave-one-out perturbations already implemented there.

## Academic integrity notes

- **Never commit synthetic output as if it were observational evidence.**
- All figures and tables in `results/` are regenerated from source data; they
  are excluded from version control (see `.gitignore`).
- If you replace the placeholder crop statistics with official NISR / MINAGRI
  figures, add the official source URL in a comment in the CSV header row.

## Reporting issues

Open a GitHub Issue with:
1. The exact command that failed.
2. The full traceback.
3. Your Python version (`python --version`) and OS.
