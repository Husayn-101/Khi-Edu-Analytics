"""Verify that the configured DATABASE_URL can connect to Postgres."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from dotenv import load_dotenv  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402


load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError("DATABASE_URL is missing. Add it to your .env file first.")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print(result.fetchone())
            print("Database connection successful.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()