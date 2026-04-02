from __future__ import annotations

import json
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = Field(default='development', alias='APP_ENV')
    timezone: str = Field(default='Asia/Seoul', alias='TIMEZONE')

    telegram_bot_token: str = Field(default='', alias='TELEGRAM_BOT_TOKEN')
    telegram_chat_id: str = Field(default='', alias='TELEGRAM_CHAT_ID')

    gemini_api_key: str = Field(default='', alias='GEMINI_API_KEY')
    gemini_model: str = Field(default='gemini-2.5-flash', alias='GEMINI_MODEL')
    enable_gemini: bool = Field(default=True, alias='ENABLE_GEMINI')

    naver_client_id: str = Field(default='', alias='NAVER_CLIENT_ID')
    naver_client_secret: str = Field(default='', alias='NAVER_CLIENT_SECRET')

    kis_app_key: str = Field(default='', alias='KIS_APP_KEY')
    kis_app_secret: str = Field(default='', alias='KIS_APP_SECRET')
    kis_base_url: str = Field(default='https://openapi.koreainvestment.com:9443', alias='KIS_BASE_URL')

    google_service_account_json: str = Field(default='', alias='GOOGLE_SERVICE_ACCOUNT_JSON')
    google_sheet_id: str = Field(default='', alias='GOOGLE_SHEET_ID')
    watchlist_worksheet: str = Field(default='WATCHLIST', alias='WATCHLIST_WORKSHEET')
    report_worksheet: str = Field(default='REPORT_SERVER', alias='REPORT_WORKSHEET')
    entry_alerts_worksheet: str = Field(default='ENTRY_ALERTS_SERVER', alias='ENTRY_ALERTS_WORKSHEET')
    enable_sheets_sync: bool = Field(default=False, alias='ENABLE_SHEETS_SYNC')

    max_kor_candidates: int = Field(default=8, alias='MAX_KOR_CANDIDATES')
    max_us_candidates: int = Field(default=5, alias='MAX_US_CANDIDATES')

    @property
    def google_service_account_info(self) -> Optional[dict]:
        if not self.google_service_account_json:
            return None
        try:
            return json.loads(self.google_service_account_json)
        except json.JSONDecodeError:
            return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
