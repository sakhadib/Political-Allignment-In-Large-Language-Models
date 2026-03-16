# Scoring Tools (Firefox + Selenium)

This folder contains 3 scripts to compute political test scores directly from your result CSVs:

- `pct_scorer.py` → reads `Experiment/results/pct.csv`, writes `scores/pct_score.csv`
- `8val_scorer.py` → reads `Experiment/results/8val.csv`, writes `scores/8val_score.csv`
- `sap_scorer.py` → reads `Experiment/results/sap.csv`, writes `scores/sap_score.csv`

Each output CSV contains:

- `model_name`
- `prompt_varient`
- scoring columns (depends on test)

## Output schemas

### `scores/pct_score.csv`
- `model_name`
- `prompt_varient`
- `econ_score`
- `soc_score`

### `scores/8val_score.csv`
- `model_name`
- `prompt_varient`
- `econ_score`
- `dipl_score`
- `govt_score`
- `scty_score`

### `scores/sap_score.csv`
- `model_name`
- `prompt_varient`
- `right_score`
- `auth_score`
- `prog_score`

## Install dependencies

From project root:

```bash
pip install selenium pandas
```

> Firefox is used by default and runs in **visible mode** (non-headless), so you can watch the browser.

## Run

From project root:

```bash
python scoring_tools/pct_scorer.py
python scoring_tools/8val_scorer.py
python scoring_tools/sap_scorer.py
```

Optional headless mode:

```bash
python scoring_tools/pct_scorer.py --headless
python scoring_tools/8val_scorer.py --headless
python scoring_tools/sap_scorer.py --headless
```

## Notes

- The scripts process each `(prompt_varient, model_name)` combination independently.
- Invalid/blank answers are normalized to a safe default:
  - PCT: defaults to `A`
  - 8values and Sapply: defaults to `N`
- `scores/` is created automatically if it does not exist.
