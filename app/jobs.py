from __future__ import annotations

import asyncio
import sys

from app.core.logging import setup_logging
from app.services.report_engine import ReportEngine


def main() -> None:
    setup_logging()
    mode = (sys.argv[1] if len(sys.argv) > 1 else 'manual').lower()
    if mode not in {'manual', 'lunch', 'evening'}:
        raise SystemExit('usage: python -m app.jobs [manual|lunch|evening]')
    engine = ReportEngine()
    asyncio.run(engine.run(mode))


if __name__ == '__main__':
    main()
