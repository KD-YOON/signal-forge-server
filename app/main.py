from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import setup_logging
from app.services.report_engine import ReportEngine

setup_logging()
engine = ReportEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title='Signal Forge Render Starter', version='0.1.0', lifespan=lifespan)


@app.get('/health')
async def health() -> dict:
    return {'ok': True}


@app.post('/run/{mode}')
async def run_report(mode: str) -> dict:
    if mode not in {'manual', 'lunch', 'evening'}:
        return {'ok': False, 'error': 'invalid mode'}
    rows = await engine.run(mode)  # type: ignore[arg-type]
    return {
        'ok': True,
        'mode': mode,
        'count': len(rows),
        'top': [
            {
                'market': r.market,
                'code': r.code,
                'name': r.name,
                'signal': r.signal,
                'score': r.score,
            }
            for r in rows[:5]
        ],
    }
