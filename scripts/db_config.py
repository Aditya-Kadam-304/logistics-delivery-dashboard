"""
db_config.py

Shared PostgreSQL connection helper. Reads credentials from .env.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_engine():
    """Returns a SQLAlchemy engine connected to the PostgreSQL database."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")

    missing = [k for k, v in {
        "DB_USER": user, "DB_PASSWORD": password, "DB_NAME": dbname
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required DB env vars: {missing}")

    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(conn_str)
