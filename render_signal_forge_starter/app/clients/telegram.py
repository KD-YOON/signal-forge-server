from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_message(self, text: str) -> None:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            logger.warning('Telegram env is missing. Skipping send.')
            return
        url = f'https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage'
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, data={'chat_id': self.settings.telegram_chat_id, 'text': text})
            response.raise_for_status()
