# Khi-Edu-Analytics

Karachi student survey analysis with a privacy-first ETL flow, reusable Python helpers, and notebook-based reporting.

## Overview

This repository is a small analytics project, not a warehouse-scale data engineering platform. It is organized to show:

- structured raw-to-cleaned-to-public data handling
- a warehouse that can run locally with SQLite for development or in Postgres in the cloud
- change-detected refreshes from the source CSV
- reproducible analysis notebooks
- a privacy-safe public export workflow
- presentation-ready charts and findings

## Architecture

```mermaid
flowchart LR
    A[Raw survey CSV] --> B[scripts/helpers.py]
	B --> C[Cleaned analysis frame]
	C --> D[data/warehouse SQLite or Postgres]
	C --> E[data/cleaned/public export]
	C --> F[notebooks/ exploration]
	F --> G[visuals/ charts]
	G --> H[README and report]
```

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/pipeline.py
python -m unittest discover -s tests
jupyter notebook
```

Use the notebooks for analysis, but prefer the cloud pipeline when you want a repeatable public export. The GitHub Actions workflow runs the ETL on a schedule against Supabase/Postgres, so your laptop does not need to stay on.

For local development only, you can still run:

```bash
python scripts/pipeline.py --watch --interval 30
```

To write into Postgres instead of local SQLite, create a `.env` file from [`.env.example`](.env.example) and set:

```bash
PIPELINE_TARGET=postgres
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

To test the Supabase or Postgres connection after creating `.env`, run:

```bash
python scripts/test_connection.py
```

## Repository Scope

This project includes:

- [scripts/helpers.py](scripts/helpers.py) for loading, cleaning, privacy checks, and summaries
- [scripts/pipeline.py](scripts/pipeline.py) for the ETL pipeline, local SQLite mode, and optional Postgres mode
- [scripts/pipeline.py](scripts/pipeline.py) for the ETL pipeline, local SQLite mode, and optional Postgres mode
- [scripts/test_connection.py](scripts/test_connection.py) for a quick Postgres connection check
- [.env.example](.env.example) for the required environment variables
- [.github/workflows/cloud-etl.yml](.github/workflows/cloud-etl.yml) for the scheduled cloud ETL job
- [sql/](sql) for warehouse SQL or schema files if you add them
- [notebooks/](notebooks) for exploration and final narrative analysis
- [visuals/](visuals) for saved figures
- [tests/](tests) for helper validation
- [.github/workflows/ci.yml](.github/workflows/ci.yml) for basic automated checks

## Privacy and Safety

This dataset is sensitive because it concerns students and includes marginalization and substance-use questions. The public repository should never contain direct identifiers or fields that can reasonably identify a respondent.

The local workflow is:

1. Keep the raw CSV on your machine.
2. Load it with `load_survey_data(...)`.
3. Create a reduced export with `prepare_public_survey_data(...)`.
4. Call `validate_public_survey_data(...)` before saving or sharing.

The repository now ignores local caches, notebook checkpoints, virtual environments, and generated outputs under `data/`.

## Data Summary

The current cleaned dataset contains 366 responses. The raw export originally contained 1,024 responses, with incomplete or invalid entries removed during cleaning.

The survey covers:

- demographics such as age, gender, and grade/class
- study habits and subject difficulty
- extracurricular participation
- marginalization and discrimination responses
- substance-use responses

## Recommended Flow

1. Push to GitHub and let [.github/workflows/cloud-etl.yml](.github/workflows/cloud-etl.yml) run the ETL in the cloud.
2. Use [scripts/pipeline.py](scripts/pipeline.py) locally only when you are developing or testing.
3. Open [notebooks/01_data_loading_cleaning.ipynb](notebooks/01_data_loading_cleaning.ipynb) to inspect the cleaning logic.
4. Use the analysis notebooks for demographics, study habits, wellbeing, and final summary work.
5. Keep final charts in [visuals/](visuals) and summarize conclusions in the executive notebook.

## Results and Conclusions

The project is strongest as a university or junior-analyst portfolio piece when the focus is on:

- transparent cleaning decisions
- a clear privacy boundary between local and public data
- concise charts with readable labels
- a short executive summary that states the main findings and limitations

It is not yet a database-backed production pipeline, so it should be presented as a reproducible analytics project rather than a complete data platform.

## Project Structure

```
Khi-Edu-Analytics/
├── data/
│   ├── raw/
│   └── cleaned/
├── notebooks/
├── report/
├── scripts/
├── sql/
├── data/
│   ├── warehouse/
│   └── state/
├── tests/
├── visuals/
├── .env.example
├── CONTRIBUTING.md
├── requirements.txt
└── README.md
```

## Environment Notes

If installation fails on a new machine, create a fresh virtual environment and reinstall from `requirements.txt`. The repo assumes Python 3.12 for CI, but the code should work on modern Python 3.11+ environments with the listed packages.

## Contribution Notes

See [CONTRIBUTING.md](CONTRIBUTING.md) for the privacy rules and validation commands used in this repository.


