"""Local ETL pipeline for the Karachi survey project.

The pipeline keeps the raw CSV on disk, loads a cleaned copy into SQLite,
and materializes a privacy-safe public export. It can also watch the source
file and refresh the warehouse when the file changes.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

from helpers import (  # noqa: E402
    DATA_DIR,
    STATE_DIR,
    WAREHOUSE_DIR,
    build_clean_survey_frame,
    build_public_survey_frame,
    get_file_fingerprint,
    get_survey_file_path,
    validate_public_survey_data,
)


RAW_SOURCE_FILENAME = "Karachi Edu Analytics Survey .csv"
WAREHOUSE_FILENAME = "karachi_edu_analytics.sqlite"
PUBLIC_EXPORT_FILENAME = "karachi_edu_analytics_public.csv"
STATE_FILENAME = "pipeline_state.json"
SOURCE_TABLE = "survey_clean"


def _get_pipeline_target(explicit_target: str | None = None) -> str:
    default_target = "postgres" if os.getenv("DATABASE_URL", "").strip() else "sqlite"
    target = (explicit_target or os.getenv("PIPELINE_TARGET") or default_target).strip().lower()
    if target not in {"sqlite", "postgres"}:
        raise ValueError("PIPELINE_TARGET must be 'sqlite' or 'postgres'")
    return target


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError("DATABASE_URL is required when PIPELINE_TARGET=postgres")
    return database_url


def _ensure_directories() -> None:
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cleaned").mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _read_state(state_path: Path) -> dict:
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {}


def _write_state(state_path: Path, state: dict) -> None:
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _get_source_metadata(source_path: Path) -> dict:
    stat_result = source_path.stat()
    return {
        "source_path": str(source_path),
        "source_mtime": stat_result.st_mtime,
        "source_size": stat_result.st_size,
        "source_fingerprint": get_file_fingerprint(source_path),
    }


def _write_to_sqlite(clean_df, warehouse_path: Path) -> None:
    connection = sqlite3.connect(warehouse_path)
    try:
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        clean_df.to_sql(SOURCE_TABLE, connection, if_exists="replace", index=False)
        connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{SOURCE_TABLE}_gender ON {SOURCE_TABLE} (gender)"
        )
        connection.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{SOURCE_TABLE}_age ON {SOURCE_TABLE} (age)"
        )
        connection.commit()
    finally:
        connection.close()


def _write_to_postgres(clean_df, database_url: str) -> None:
    from sqlalchemy import create_engine

    engine = create_engine(database_url)
    try:
        clean_df.to_sql(SOURCE_TABLE, engine, if_exists="replace", index=False)
        with engine.begin() as connection:
            connection.exec_driver_sql(
                f"CREATE INDEX IF NOT EXISTS idx_{SOURCE_TABLE}_gender ON {SOURCE_TABLE} (gender)"
            )
            connection.exec_driver_sql(
                f"CREATE INDEX IF NOT EXISTS idx_{SOURCE_TABLE}_age ON {SOURCE_TABLE} (age)"
            )
    finally:
        engine.dispose()


def extract_transform_load(
    source_filename: str = RAW_SOURCE_FILENAME,
    data_dir: Path = DATA_DIR,
    warehouse_dir: Path = WAREHOUSE_DIR,
    state_dir: Path = STATE_DIR,
    target: str | None = None,
) -> dict:
    """Run the local ETL pipeline and persist both warehouse and public outputs."""
    _ensure_directories()
    pipeline_target = _get_pipeline_target(target)
    warehouse_path = Path(warehouse_dir) / WAREHOUSE_FILENAME
    public_data_path = Path(data_dir) / "cleaned" / PUBLIC_EXPORT_FILENAME
    state_path = Path(state_dir) / STATE_FILENAME
    source_path = get_survey_file_path(filename=source_filename, data_dir=data_dir)

    clean_df = build_clean_survey_frame(filename=source_filename, data_dir=data_dir)
    public_df = build_public_survey_frame(filename=source_filename, data_dir=data_dir)
    validate_public_survey_data(public_df)

    Path(warehouse_dir).mkdir(parents=True, exist_ok=True)
    public_data_path.parent.mkdir(parents=True, exist_ok=True)
    Path(state_dir).mkdir(parents=True, exist_ok=True)

    if pipeline_target == "postgres":
        _write_to_postgres(clean_df, _get_database_url())
    else:
        _write_to_sqlite(clean_df, warehouse_path)

    public_df.to_csv(public_data_path, index=False)

    state = {
        **_get_source_metadata(source_path),
        "rows_loaded": int(len(clean_df)),
        "public_rows_written": int(len(public_df)),
        "pipeline_target": pipeline_target,
        "warehouse_path": str(warehouse_path) if pipeline_target == "sqlite" else "postgres",
        "public_export_path": str(public_data_path),
        "source_table": SOURCE_TABLE,
        "last_refresh_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write_state(state_path, state)
    return state


def refresh_if_source_changed(
    source_filename: str = RAW_SOURCE_FILENAME,
    data_dir: Path = DATA_DIR,
    warehouse_dir: Path = WAREHOUSE_DIR,
    state_dir: Path = STATE_DIR,
    target: str | None = None,
) -> dict | None:
    """Refresh the ETL outputs only if the source file has changed."""
    source_path = get_survey_file_path(filename=source_filename, data_dir=data_dir)
    state_path = Path(state_dir) / STATE_FILENAME
    current_state = _read_state(state_path)
    current_metadata = _get_source_metadata(source_path)

    if (
        current_state.get("source_fingerprint") == current_metadata["source_fingerprint"]
        and current_state.get("source_size") == current_metadata["source_size"]
    ):
        return None

    return extract_transform_load(
        source_filename=source_filename,
        data_dir=data_dir,
        warehouse_dir=warehouse_dir,
        state_dir=state_dir,
        target=target,
    )


def watch_source(
    source_filename: str = RAW_SOURCE_FILENAME,
    interval_seconds: int = 30,
    data_dir: Path = DATA_DIR,
    warehouse_dir: Path = WAREHOUSE_DIR,
    state_dir: Path = STATE_DIR,
    target: str | None = None,
) -> None:
    """Poll the raw source and refresh outputs when the file changes."""
    print(f"Watching {source_filename} for changes every {interval_seconds}s...")
    while True:
        refreshed_state = refresh_if_source_changed(
            source_filename=source_filename,
            data_dir=data_dir,
            warehouse_dir=warehouse_dir,
            state_dir=state_dir,
            target=target,
        )
        if refreshed_state is not None:
            print(
                "Refreshed warehouse and public export "
                f"({refreshed_state['rows_loaded']} rows loaded)."
            )
        time.sleep(interval_seconds)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Karachi survey ETL pipeline.")
    parser.add_argument(
        "--source-file",
        default=RAW_SOURCE_FILENAME,
        help="Raw survey CSV filename inside the data directory.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Poll for source file changes and refresh outputs when needed.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Polling interval in seconds when --watch is enabled.",
    )
    parser.add_argument(
        "--target",
        default=None,
        choices=["sqlite", "postgres"],
        help="Override PIPELINE_TARGET for the current run.",
    )
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    if args.watch:
        watch_source(source_filename=args.source_file, interval_seconds=args.interval, target=args.target)
        return

    state = extract_transform_load(source_filename=args.source_file, target=args.target)
    print(
        "Warehouse refreshed: "
        f"{state['rows_loaded']} rows loaded into {state['warehouse_path']}"
    )
    print(f"Pipeline target: {state['pipeline_target']}")
    print(f"Public export written to {state['public_export_path']}")


if __name__ == "__main__":
    main()