"""Adapters between external data tools and the specialist pipelines."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd


NEWS_ANALYSIS_COLUMNS = (
    "ticker",
    "published_at",
    "headline",
    "source",
    "url",
    "text",
)


def news_records_to_dataframe(
    records: Iterable[Mapping[str, Any]],
) -> pd.DataFrame:
    """Convert normalized tool records to Russell's news-chain contract.

    Records without a headline, URL, publication time, or article text are
    excluded because they cannot support a source-grounded summary.
    """
    rows = []

    for record in records:
        publisher = record.get("publisher")
        source = (
            publisher.strip()
            if isinstance(publisher, str) and publisher.strip()
            else str(record.get("source") or "").strip()
        )
        summary = record.get("summary")
        text = summary.strip() if isinstance(summary, str) else ""
        if not text:
            text = str(
                record.get("headline") or record.get("title") or ""
            ).strip()

        rows.append(
            {
                "ticker": str(record.get("ticker") or "").strip().upper(),
                "published_at": record.get("published_at"),
                "headline": str(
                    record.get("headline") or record.get("title") or ""
                ).strip(),
                "source": source,
                "url": str(record.get("url") or "").strip(),
                "text": text,
            }
        )

    frame = pd.DataFrame(rows, columns=NEWS_ANALYSIS_COLUMNS)
    if frame.empty:
        return frame

    frame["published_at"] = pd.to_datetime(
        frame["published_at"],
        errors="coerce",
        utc=True,
    )
    for column in ("ticker", "headline", "source", "url", "text"):
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace("", pd.NA)

    return (
        frame.dropna(subset=NEWS_ANALYSIS_COLUMNS)
        .drop_duplicates(subset=["url"])
        .reset_index(drop=True)
    )
