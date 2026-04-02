from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import Quote

logger = logging.getLogger(__name__)


class KISClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._token: str = ''
        self._expires_at: datetime | None = None

    async def get_access_token(self) -> str:
        if self._token and self._expires_at and datetime.utcnow() < self._expires_at:
            return self._token
        if not self.settings.kis_app_key or not self.settings.kis_app_secret:
            raise RuntimeError('KIS env is missing')
        url = f'{self.settings.kis_base_url}/oauth2/tokenP'
        payload = {
            'grant_type': 'client_credentials',
            'appkey': self.settings.kis_app_key,
            'appsecret': self.settings.kis_app_secret,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        token = data.get('access_token')
        if not token:
            raise RuntimeError(f'KIS token failed: {data}')
        expires_in = int(data.get('expires_in', 86400))
        self._token = token
        self._expires_at = datetime.utcnow() + timedelta(seconds=max(expires_in - 60, 60))
        return self._token

    async def get_domestic_quote(self, code: str, name: str) -> Quote:
        token = await self.get_access_token()
        url = f'{self.settings.kis_base_url}/uapi/domestic-stock/v1/quotations/inquire-price'
        headers = {
            'authorization': f'Bearer {token}',
            'appkey': self.settings.kis_app_key,
            'appsecret': self.settings.kis_app_secret,
            'tr_id': 'FHKST01010100',
            'content-type': 'application/json',
        }
        params = {'FID_COND_MRKT_DIV_CODE': 'J', 'FID_INPUT_ISCD': code}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        output = data.get('output', {})
        price = float(output.get('stck_prpr') or 0)
        prev_close = float(output.get('stck_sdpr') or 0)
        change_pct = float(output.get('prdy_ctrt') or 0)
        return Quote(
            market='KOR',
            code=code,
            name=name,
            price=price,
            prev_close=prev_close,
            change_pct=change_pct,
            open=float(output.get('stck_oprc') or 0),
            high=float(output.get('stck_hgpr') or 0),
            low=float(output.get('stck_lwpr') or 0),
            volume=float(output.get('acml_vol') or 0),
            source='KIS',
        )
