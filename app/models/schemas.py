from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Market = Literal['KOR', 'US']
RunMode = Literal['manual', 'lunch', 'evening']


@dataclass(slots=True)
class WatchItem:
    market: Market
    code: str
    name: str
    enabled: bool = True


@dataclass(slots=True)
class Quote:
    market: Market
    code: str
    name: str
    price: float
    prev_close: float
    change_pct: float
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: float = 0.0
    source: str = ''


@dataclass(slots=True)
class NewsItem:
    source: str
    market: Market
    code: str
    title: str
    summary: str = ''
    url: str = ''
    published_at: str = ''
    language: str = 'ko'
    relevance_score: float = 0.0


@dataclass(slots=True)
class CandidateReport:
    market: Market
    code: str
    name: str
    price: float
    prev_close: float
    change_pct: float
    news_count: int
    news_keywords: str
    news_summary: str
    sentiment_score: int
    sentiment_confidence: int
    signal: str
    reason: str
    source: str = ''
    score: int = 0
    action: str = ''
    lower: float = 0.0
    upper: float = 0.0
    suggested_buy: float = 0.0
    extras: dict = field(default_factory=dict)
