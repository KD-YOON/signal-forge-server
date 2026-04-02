from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import NewsItem

logger = logging.getLogger(__name__)


class NaverNewsClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, market: str, code: str, query: str, display: int = 5) -> list[NewsItem]:
        if not self.settings.naver_client_id or not self.settings.naver_client_secret:
            return []
        url = 'https://openapi.naver.com/v1/search/news.json'
        headers = {
            'X-Naver-Client-Id': self.settings.naver_client_id,
            'X-Naver-Client-Secret': self.settings.naver_client_secret,
        }
        params = {'query': query, 'display': display, 'sort': 'date'}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        out: list[NewsItem] = []
        for item in data.get('items', []):
            out.append(
                NewsItem(
                    source='NAVER',
                    market=market,  # type: ignore[arg-type]
                    code=code,
                    title=_strip_html(item.get('title', '')),
                    summary=_strip_html(item.get('description', '')),
                    url=item.get('link', ''),
                    published_at=item.get('pubDate', ''),
                    language='ko',
                )
            )
        return out


def _strip_html(text: str) -> str:
    import re
    return re.sub(r'<[^>]+>', '', str(text or '')).strip()
