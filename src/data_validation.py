from __future__ import annotations
from pathlib import Path
import pandas as pd

REQUIRED_NEWS_COLUMNS = {
    "ticker",
    "published_at",
    "headline",
    "source",
    "url",
}

def validate_news_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate news metadata and return a cleaned copy."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("News input must be a Pandas DataFrame.")

    missing_columns = REQUIRED_NEWS_COLUMNS - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df.copy()

    text_columns = ("ticker", "headline", "source", "url")

    for column in text_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        cleaned[column] = cleaned[column].replace("", pd.NA)

    cleaned["ticker"] = cleaned["ticker"].str.upper()

    cleaned["published_at"] = pd.to_datetime(
        cleaned["published_at"],
        errors="coerce",
        utc=True,
    )

    cleaned = cleaned.dropna(
        subset=["ticker", "published_at", "headline", "source", "url"]
    )

    cleaned = cleaned.drop_duplicates(subset=["url"]).reset_index(drop=True)

    return cleaned

def ensure_data_directories(project_root: Path) -> tuple[Path, Path]:
    """Create and return the raw and processed local data directories."""
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    return raw_dir, processed_dir