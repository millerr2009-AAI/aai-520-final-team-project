from __future__ import annotations
from pathlib import Path
import duckdb
import pandas as pd

ARTICLE_ID_SEQUENCE_SQL = """
CREATE SEQUENCE IF NOT EXISTS article_id_sequence START 1
"""


ARTICLES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    article_id BIGINT PRIMARY KEY DEFAULT nextval('article_id_sequence'),
    ticker VARCHAR NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    headline VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

def get_connection(database_path: Path) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection and ensure the required database objects exist."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(database_path))
    connection.execute(ARTICLE_ID_SEQUENCE_SQL)
    connection.execute(ARTICLES_TABLE_SQL)

    return connection

def insert_articles(
    connection: duckdb.DuckDBPyConnection,
    articles: pd.DataFrame,
) -> int:
    """Insert validated articles and return the number of new rows inserted."""
    if articles.empty:
        return 0

    before_count = connection.execute(
        "SELECT COUNT(*) FROM articles"
    ).fetchone()[0]

    connection.register("incoming_articles", articles)

    try:
        connection.execute("""
            INSERT INTO articles (
                ticker,
                published_at,
                headline,
                source,
                url
            )
            SELECT
                ticker,
                published_at,
                headline,
                source,
                url
            FROM incoming_articles
            ON CONFLICT (url) DO NOTHING
        """)
    finally:
        connection.unregister("incoming_articles")

    after_count = connection.execute(
        "SELECT COUNT(*) FROM articles"
    ).fetchone()[0]

    return after_count - before_count

def fetch_articles(
    connection: duckdb.DuckDBPyConnection,
    ticker: str | None = None,
) -> pd.DataFrame:
    """Return stored articles, optionally limited to one ticker symbol."""
    if ticker is None:
        return connection.execute("""
            SELECT
                article_id,
                ticker,
                published_at,
                headline,
                source,
                url,
                ingested_at
            FROM articles
            ORDER BY published_at DESC, article_id DESC
        """).df()

    return connection.execute("""
        SELECT
            article_id,
            ticker,
            published_at,
            headline,
            source,
            url,
            ingested_at
        FROM articles
        WHERE ticker = ?
        ORDER BY published_at DESC, article_id DESC
    """, [ticker.upper().strip()]).df()