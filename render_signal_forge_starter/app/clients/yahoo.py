from __future__ import annotations

import logging

import yfinance as yf

from app.models.schemas import NewsItem, Quote

logger = logging.getLogger(__name__)


class YahooClient:
    async def get_quote(self, code: str, name: str) -> Quote:
        ticker = yf.Ticker(code)
        info = ticker.fast_info
        price = float(info.get('lastPrice') or 0)
        prev_close = float(info.get('previousClose') or 0)
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
        return Quote(
            market='US',
            code=code,
            name=name,
            price=price,
            prev_close=prev_close,
            change_pct=change_pct,
            open=float(info.get('open') or 0),
            high=float(info.get('dayHigh') or 0),
            low=float(info.get('dayLow') or 0),
            volume=float(info.get('lastVolume') or 0),
            source='YAHOO',
        )

    async def get_news(self, code: str) -> list[NewsItem]:
        ticker = yf.Ticker(code)
        out: list[NewsItem] = []
        for item in (ticker.news or [])[:5]:
            content = item.get('content', {}) if isinstance(item, dict) else {}
            out.append(
                NewsItem(
                    source='YAHOO',
                    market='US',
                    code=code,
                    title=content.get('title', '') or item.get('title', ''),
                    summary=content.get('summary', '') or '',
                    url=content.get('canonicalUrl', {}).get('url', '') if isinstance(content.get('canonicalUrl'), dict) else '',
                    published_at=str(content.get('pubDate', '')),
                    language='en',
                )
            )
        return out
