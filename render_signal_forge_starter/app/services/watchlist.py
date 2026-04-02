from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import WatchItem


def load_watchlist_from_file(path: str = 'watchlist.sample.json') -> list[WatchItem]:
    p = Path(path)
    if not p.exists():
        return []
    raw = json.loads(p.read_text(encoding='utf-8'))
    items: list[WatchItem] = []
    for row in raw:
        if not row.get('enabled', True):
            continue
        items.append(
            WatchItem(
                market=str(row.get('market', 'KOR')).upper(),  # type: ignore[arg-type]
                code=str(row.get('code', '')).upper(),
                name=str(row.get('name', '')),
                enabled=bool(row.get('enabled', True)),
            )
        )
    return items
