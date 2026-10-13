from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectConfig:
    """Shared configuration for the financial research workflow."""

    # Demo / workflow defaults
    demo_ticker: str = "NVDA"
    max_news_articles: int = 15
    min_evaluation_score: int = 4
    max_revisions: int = 1

    # Tool identifiers used by the planner/router
    financial_tool_name: str = "financial_data"
    news_tool_name: str = "news_data"

    # Data windows
    price_period: str = "1y"
    price_interval: str = "1d"

    # Persistence
    memory_table: str = "investment_agent_memory"
    research_runs_table: str = "investment_agent_runs"

    # Model placeholders
    planner_model: str = "YOUR_MODEL_NAME"
    analyst_model: str = "YOUR_MODEL_NAME"
    evaluator_model: str = "YOUR_MODEL_NAME"

CONFIG = ProjectConfig()

def normalize_ticker(ticker: str) -> str:
    """Normalize and validate a stock ticker string."""
    if not ticker or not isinstance(ticker, str):
        raise ValueError("ticker must be a non-empty string")

    normalized = ticker.strip().upper()

    if not normalized:
        raise ValueError("ticker must be a non-empty string")

    return normalized