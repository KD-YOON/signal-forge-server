from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def summarize_news(self, subject: str, joined_news: str) -> dict[str, Any]:
        if not self.settings.enable_gemini or not self.settings.gemini_api_key:
            return {'summary': '', 'sentiment_score': 0, 'confidence': 50, 'keywords': ''}

        url = (
            f'https://generativelanguage.googleapis.com/v1beta/models/'
            f'{self.settings.gemini_model}:generateContent'
        )
        prompt = (
            'Return strict JSON only. '\
            '{"summary":"<=2 sentences in Korean","sentiment_score":-100~100,'
            '"confidence":0~100,"keywords":"comma separated"}.\n\n'
            f'Subject: {subject}\nNews:\n{joined_news}'
        )
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json'},
        }
        headers = {'x-goog-api-key': self.settings.gemini_api_key, 'Content-Type': 'application/json'}
        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        text = ''
        try:
            text = data['candidates'][0]['content']['parts'][0]['text']
        except Exception as exc:  # noqa: BLE001
            logger.warning('Gemini parse failed: %s', exc)
            return {'summary': '', 'sentiment_score': 0, 'confidence': 50, 'keywords': ''}
        try:
            import json
            return json.loads(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning('Gemini json decode failed: %s', exc)
            return {'summary': text[:160], 'sentiment_score': 0, 'confidence': 50, 'keywords': ''}
