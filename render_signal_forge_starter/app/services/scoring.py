from __future__ import annotations

from app.models.schemas import CandidateReport, NewsItem, Quote, WatchItem


def build_candidate(item: WatchItem, quote: Quote, news: list[NewsItem], gemini: dict) -> CandidateReport:
    summary = str(gemini.get('summary') or _fallback_summary(news))
    sentiment_score = int(gemini.get('sentiment_score') or 0)
    sentiment_confidence = int(gemini.get('confidence') or 50)
    keywords = str(gemini.get('keywords') or _keywords(news))

    score = 50
    reason_bits: list[str] = []

    if quote.change_pct > 0:
        score += min(int(quote.change_pct), 8)
        reason_bits.append('가격강세')
    if sentiment_score > 20:
        score += 10
        reason_bits.append('뉴스긍정')
    if len(news) >= 3:
        score += 5
        reason_bits.append('뉴스풍부')

    signal = 'WATCH'
    action = '관망'
    if score >= 70:
        signal = 'ENTRY'
        action = '분할진입 검토'
    elif score >= 60:
        signal = 'READY'
        action = '관심구간 확인'

    suggested_buy = round(quote.prev_close * 0.95, 2) if quote.prev_close else 0.0
    lower = round(suggested_buy * 0.988, 2) if suggested_buy else 0.0
    upper = round(suggested_buy * 1.012, 2) if suggested_buy else 0.0

    return CandidateReport(
        market=item.market,
        code=item.code,
        name=item.name,
        price=quote.price,
        prev_close=quote.prev_close,
        change_pct=quote.change_pct,
        news_count=len(news),
        news_keywords=keywords,
        news_summary=summary,
        sentiment_score=sentiment_score,
        sentiment_confidence=sentiment_confidence,
        signal=signal,
        reason=', '.join(reason_bits) if reason_bits else '중립',
        source=quote.source,
        score=score,
        action=action,
        lower=lower,
        upper=upper,
        suggested_buy=suggested_buy,
        extras={'news_sources': sorted({n.source for n in news})},
    )


def _fallback_summary(news: list[NewsItem]) -> str:
    if not news:
        return '뉴스 없음'
    return ' / '.join(n.title for n in news[:2])[:180]


def _keywords(news: list[NewsItem]) -> str:
    if not news:
        return ''
    text = ' '.join(f'{n.title} {n.summary}' for n in news)
    keywords = []
    for key in ['실적', '수주', '계약', 'AI', '반도체', '전기차', 'guidance', 'earnings', 'partnership']:
        if key.lower() in text.lower():
            keywords.append(key)
    return ', '.join(keywords[:5])
