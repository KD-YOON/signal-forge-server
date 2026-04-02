from __future__ import annotations

import asyncio
import logging

from app.clients.gemini import GeminiClient
from app.clients.kis import KISClient
from app.clients.naver import NaverNewsClient
from app.clients.telegram import TelegramClient
from app.clients.yahoo import YahooClient
from app.models.schemas import CandidateReport, RunMode, WatchItem
from app.services.scoring import build_candidate
from app.services.watchlist import load_watchlist_from_file

logger = logging.getLogger(__name__)


class ReportEngine:
    def __init__(self) -> None:
        self.kis = KISClient()
        self.naver = NaverNewsClient()
        self.yahoo = YahooClient()
        self.gemini = GeminiClient()
        self.telegram = TelegramClient()

    async def run(self, mode: RunMode) -> list[CandidateReport]:
        watchlist = load_watchlist_from_file()
        tasks = [self._analyze_item(item) for item in watchlist]
        results = [r for r in await asyncio.gather(*tasks, return_exceptions=False) if r]
        results.sort(key=lambda x: x.score, reverse=True)
        message = self._build_message(mode, results)
        await self.telegram.send_message(message)
        return results

    async def _analyze_item(self, item: WatchItem) -> CandidateReport | None:
        try:
            if item.market == 'US':
                quote = await self.yahoo.get_quote(item.code, item.name)
                news = await self.yahoo.get_news(item.code)
                news.extend(await self.naver.search(item.market, item.code, item.name, display=2))
            else:
                quote = await self.kis.get_domestic_quote(item.code, item.name)
                news = await self.naver.search(item.market, item.code, item.name, display=5)

            joined_news = '\n'.join(f'- {n.title} | {n.summary}' for n in news[:5])
            gemini = await self.gemini.summarize_news(item.name, joined_news) if news else {}
            return build_candidate(item, quote, news, gemini)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Analyze failed for %s/%s: %s', item.market, item.code, exc)
            return None

    def _build_message(self, mode: RunMode, rows: list[CandidateReport]) -> str:
        title = {'manual': '수동', 'lunch': '점심', 'evening': '저녁'}.get(mode, mode)
        lines = [f'🔍 Signal Forge Render 스타터 | {title} 리포트', '']
        if not rows:
            lines.append('후보가 없습니다.')
            return '\n'.join(lines)

        for idx, row in enumerate(rows[:8], start=1):
            lines.append(f'{idx}. {row.name} ({row.code}/{row.market})')
            lines.append(f'   가격 {row.price:.2f} | 전일 {row.prev_close:.2f} | 등락 {row.change_pct:.2f}%')
            lines.append(f'   신호 {row.signal} | 점수 {row.score} | 행동 {row.action}')
            if row.suggested_buy:
                lines.append(f'   제안매수가 {row.suggested_buy:.2f} | 관심구간 {row.lower:.2f} ~ {row.upper:.2f}')
            if row.news_keywords:
                lines.append(f'   뉴스핵심 {row.news_keywords}')
            if row.news_summary:
                lines.append(f'   뉴스요약 {row.news_summary}')
            lines.append(f'   감성 {row.sentiment_score} / 신뢰도 {row.sentiment_confidence} | 기사수 {row.news_count}')
            lines.append('')
        return '\n'.join(lines).strip()
