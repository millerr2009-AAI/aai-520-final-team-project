from __future__ import annotations
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
import pandas as pd
import yfinance as yf
from src.config import CONFIG, normalize_ticker


def _safe_value(value: Any) -> Any:
    """Convert common Pandas/NumPy values into JSON-friendly Python values."""
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, datetime):
        return value.isoformat()

    return value

def dataframe_to_records(
    df: pd.DataFrame | None,
    limit: int | None = None,
) -> list[dict]:
    """Convert a DataFrame into records, including its index."""
    if df is None or df.empty:
        return []

    work = df.copy()

    if limit is not None:
        work = work.tail(limit)

    work = work.reset_index()

    records = []
    for row in work.to_dict(orient="records"):
        records.append({key: _safe_value(value) for key, value in row.items()})

    return records

def get_financial_data(
    ticker: str,
    period: str = CONFIG.price_period,
    interval: str = CONFIG.price_interval,
) -> dict:
    """Retrieve company information, prices, and financial statements."""
    symbol = normalize_ticker(ticker)
    company = yf.Ticker(symbol)

    history = company.history(
        period=period,
        interval=interval,
        auto_adjust=False,
    )

    try:
        info = company.info or {}
    except Exception:
        info = {}

    try:
        income_stmt = company.income_stmt
    except Exception:
        income_stmt = pd.DataFrame()

    try:
        balance_sheet = company.balance_sheet
    except Exception:
        balance_sheet = pd.DataFrame()

    try:
        cash_flow = company.cashflow
    except Exception:
        cash_flow = pd.DataFrame()

    if history.empty:
        raise ValueError(f"No price history returned for ticker '{symbol}'.")

    latest_close = (
        _safe_value(history["Close"].iloc[-1])
        if "Close" in history
        else None
    )
    first_close = (
        _safe_value(history["Close"].iloc[0])
        if "Close" in history
        else None
    )

    period_return = None
    if first_close not in (None, 0) and latest_close is not None:
        period_return = (latest_close / first_close) - 1

    selected_info_keys = [
        "shortName",
        "longName",
        "sector",
        "industry",
        "marketCap",
        "currency",
        "exchange",
        "quoteType",
        "trailingPE",
        "forwardPE",
        "priceToSalesTrailing12Months",
        "profitMargins",
        "operatingMargins",
        "returnOnEquity",
        "debtToEquity",
        "revenueGrowth",
        "earningsGrowth",
        "freeCashflow",
        "totalCash",
        "totalDebt",
    ]

    company_info = {
        key: _safe_value(info.get(key))
        for key in selected_info_keys
        if key in info
    }

    return {
        "ticker": symbol,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance via yfinance",
        "price_summary": {
            "period": period,
            "interval": interval,
            "first_close": first_close,
            "latest_close": latest_close,
            "period_return": period_return,
            "rows": int(len(history)),
        },
        "company_info": company_info,
        "price_history": dataframe_to_records(history),
        "income_statement": dataframe_to_records(income_stmt.T),
        "balance_sheet": dataframe_to_records(balance_sheet.T),
        "cash_flow": dataframe_to_records(cash_flow.T),
    }

def _extract_news_item(item: dict) -> dict:
    """Normalize the news response shapes handled in Rogelio's notebook."""
    content = (
        item.get("content")
        if isinstance(item.get("content"), dict)
        else item
    )

    title = content.get("title")

    publisher = content.get("provider", {})
    if isinstance(publisher, dict):
        publisher = publisher.get("displayName") or publisher.get("name")
    publisher = publisher or content.get("publisher")

    published_at = (
        content.get("pubDate")
        or content.get("displayTime")
        or content.get("providerPublishTime")
    )
    if isinstance(published_at, (int, float)):
        published_at = datetime.fromtimestamp(
            published_at,
            tz=timezone.utc,
        ).isoformat()

    url = None
    canonical = content.get("canonicalUrl")
    if isinstance(canonical, dict):
        url = canonical.get("url")

    url = (
        url
        or content.get("link")
        or content.get("url")
        or (
            content.get("clickThroughUrl", {}).get("url")
            if isinstance(content.get("clickThroughUrl"), dict)
            else None
        )
    )

    summary = (
        content.get("summary")
        or content.get("description")
        or content.get("snippet")
    )

    return {
        "title": title,
        "publisher": publisher,
        "published_at": published_at,
        "url": url,
        "summary": summary,
    }

def get_news_data(
    ticker: str,
    limit: int = CONFIG.max_news_articles,
) -> list[dict]:
    """Retrieve and normalize news items for a ticker."""
    symbol = normalize_ticker(ticker)
    company = yf.Ticker(symbol)

    ticker_error = None
    try:
        raw_news = company.news or []
    except Exception as exc:
        ticker_error = exc
        raw_news = []

    # Ticker.news is intermittently unavailable. Search uses Yahoo's same
    # public feed and gives the demo a second retrieval path.
    if not raw_news and hasattr(yf, "Search"):
        try:
            search = yf.Search(
                f"{symbol} stock",
                news_count=limit,
                enable_fuzzy_query=False,
            )
            raw_news = search.news or []
        except Exception as exc:
            if ticker_error is not None:
                raise RuntimeError(
                    f"Unable to retrieve news for '{symbol}' using ticker "
                    f"or search endpoints: {ticker_error}; {exc}"
                ) from exc
            raise RuntimeError(
                f"Unable to retrieve news for '{symbol}': {exc}"
            ) from exc

    if not raw_news and ticker_error is not None:
        raise RuntimeError(
            f"Unable to retrieve news for '{symbol}': {ticker_error}"
        ) from ticker_error

    normalized = []
    seen = set()

    for item in raw_news:
        article = _extract_news_item(item)

        title = (article.get("title") or "").strip()
        url = article.get("url")

        if not title:
            continue

        dedupe_key = (title.lower(), url)
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        normalized.append({
            "ticker": symbol,
            "source": "Yahoo Finance via yfinance",
            **article,
        })

        if len(normalized) >= limit:
            break

    return normalized

TOOLS: dict[str, Callable[..., Any]] = {
    CONFIG.financial_tool_name: get_financial_data,
    CONFIG.news_tool_name: get_news_data,
}

def execute_tool(tool_name: str, ticker: str, **kwargs: Any) -> Any:
    """Execute a registered data tool by name."""
    if tool_name not in TOOLS:
        raise KeyError(
            f"Unknown tool '{tool_name}'. "
            f"Available tools: {sorted(TOOLS.keys())}"
        )

    return TOOLS[tool_name](ticker=ticker, **kwargs)