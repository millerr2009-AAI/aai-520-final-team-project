# Project Notes

## Working Title
News Analysis Pipeline for Financial Market Research

## Goal
Build a reproducible local pipeline that collects, stores, cleans, and analyzes financial-news data for selected companies.

## Initial Technical Stack
- Python 3.13
- Pandas 2.2.3
- NumPy 2.5.3
- DuckDB 1.5.6
- Jupyter Notebook
- yfinance for financial-data retrieval

## Data Handling Rules
- Keep downloaded source data in `data/raw/`.
- Keep cleaned and derived datasets in `data/processed/`.
- Keep local databases out of version control.
- Verify outputs before deciding whether to commit or push any work.
- Do not commit API keys, tokens, or `.env` files.

## Current Status
- Local environment setup and DuckDB/Pandas/Jupyter verification complete.
- Configuration, data tools, validation, database, and ingestion code extracted into `src/`.
- Syntax and import checks passed for `src/config.py` and `src/data_tools.py`.
- yfinance dependency added and committed for financial-data retrieval.
- NVDA financial retrieval returned price history, company information, and financial statements.
- Ticker-based news retrieval returned HTTP 404 in local testing and remains unresolved.
- Search-based news retrieval returned items, but the displayed samples lacked summaries; it has not been integrated as a replacement.
- End-to-end news ingestion and model-based analysis remain to be verified.
