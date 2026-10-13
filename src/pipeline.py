from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.data_validation import validate_news_dataframe
from src.database import get_connection, insert_articles

def ingest_news_dataframe(
    articles: pd.DataFrame,
    database_path: Path,
) -> dict[str, int]:
    """Validate and store news articles in a local DuckDB database."""
    received_rows = len(articles)
    validated_articles = validate_news_dataframe(articles)
    valid_rows = len(validated_articles)

    connection = get_connection(database_path)

    try:
        inserted_rows = insert_articles(connection, validated_articles)
    finally:
        connection.close()

    return {
        "received_rows": received_rows,
        "valid_rows": valid_rows,
        "inserted_rows": inserted_rows,
    }