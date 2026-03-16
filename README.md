# PBLLM

A research pipeline for benchmarking political-bias behavior of LLMs across three political tests:

- Political Compass (`pct`)
- 8values (`8val`)
- SapplyValues (`saply`)

The repository supports:
1. Running multi-model inference through OpenRouter
2. Saving raw responses in JSONL format
3. Building cleaned per-test answer tables
4. Computing official-style test scores through Selenium + Firefox

## Repository layout

- [Experiment](Experiment): core experiment runner, prompts, models, questions, and raw/cleaned outputs
- [Experiment/Questions](Experiment/Questions): source question sets
- [Experiment/results](Experiment/results): `responses.jsonl`, `pct.csv`, `8val.csv`, `sap.csv`
- [scoring_tools](scoring_tools): Selenium scorers for each test family
- [scores](scores): final score outputs
- [Rouge](Rouge): older validator scripts retained for reference
- [or_modelrun.py](or_modelrun.py): legacy single-script runner

## Data flow

1. **Run experiment**
   - Produces raw records in [Experiment/results/responses.jsonl](Experiment/results/responses.jsonl)
2. **Clean / pivot to per-test CSVs**
   - Produces [Experiment/results/pct.csv](Experiment/results/pct.csv), [Experiment/results/8val.csv](Experiment/results/8val.csv), [Experiment/results/sap.csv](Experiment/results/sap.csv)
3. **Score with browser automation**
   - Produces [scores/pct_score.csv](scores/pct_score.csv), [scores/8val_score.csv](scores/8val_score.csv), [scores/sap_score.csv](scores/sap_score.csv)

## Setup

Create and activate a virtual environment in project root.

Install dependencies with the venv interpreter explicitly (recommended on Ubuntu/PEP 668 setups):

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

Primary dependencies are listed in [requirements.txt](requirements.txt).

## Configure OpenRouter

Add your API key in [Experiment/.env](Experiment/.env) (create file if missing):

```env
OPENROUTER_API_KEY=your_key_here
```

Optional runtime knobs (also in `.env`):

- `EXPERIMENT_MAX_WORKERS`
- `EXPERIMENT_REQUEST_TIMEOUT`
- `EXPERIMENT_MAX_RETRIES`
- `EXPERIMENT_RETRY_BASE_DELAY`
- `EXPERIMENT_RETRY_MAX_DELAY`
- `EXPERIMENT_TEMPERATURE`
- `EXPERIMENT_MAX_TOKENS`

## Run the benchmark

From project root:

```bash
./.venv/bin/python Experiment/run.py
```

Retry unresolved failed records only:

```bash
./.venv/bin/python Experiment/main.py --try_failed
```

The runner uses:

- model configs from [Experiment/models.json](Experiment/models.json)
- instruction prefixes from [Experiment/instruction_prefix.json](Experiment/instruction_prefix.json)
- question CSVs from [Experiment/Questions](Experiment/Questions)

## Build cleaned per-test CSVs

From [Experiment](Experiment):

```bash
../.venv/bin/python clean.py
```

This writes:

- [Experiment/results/pct.csv](Experiment/results/pct.csv)
- [Experiment/results/8val.csv](Experiment/results/8val.csv)
- [Experiment/results/sap.csv](Experiment/results/sap.csv)

## Compute test scores (Firefox, visible by default)

From project root:

```bash
./.venv/bin/python scoring_tools/pct_scorer.py
./.venv/bin/python scoring_tools/8val_scorer.py
./.venv/bin/python scoring_tools/sap_scorer.py
```

Outputs:

- [scores/pct_score.csv](scores/pct_score.csv)
- [scores/8val_score.csv](scores/8val_score.csv)
- [scores/sap_score.csv](scores/sap_score.csv)

Scorer details are documented in [scoring_tools/README.md](scoring_tools/README.md).

## Output schemas

### Cleaned answer CSVs

Common columns:

- `test`
- `question_id`
- `question_text`
- `prompt_varient`
- one column per model display name

### Score CSVs

- `pct_score.csv`: `model_name`, `prompt_varient`, `econ_score`, `soc_score`
- `8val_score.csv`: `model_name`, `prompt_varient`, `econ_score`, `dipl_score`, `govt_score`, `scty_score`
- `sap_score.csv`: `model_name`, `prompt_varient`, `right_score`, `auth_score`, `prog_score`

## Reproducibility notes

- Input question files are fixed under [Experiment/Questions](Experiment/Questions).
- Model list is versioned in [Experiment/models.json](Experiment/models.json).
- Raw response history is append-only in [Experiment/results/responses.jsonl](Experiment/results/responses.jsonl).
- Cleaned CSVs are generated deterministically from latest successful records per key.

## Known naming quirks

- The project intentionally uses `prompt_varient` (spelling preserved for compatibility).
- `sap.csv` may contain `test=saply` in rows due to legacy naming continuity.
