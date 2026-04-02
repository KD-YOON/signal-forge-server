# Signal Forge Render Starter

앱스스크립트 시간초과를 피하려고 만든 **Render 배치형 스타터**입니다.

## 이 버전에서 되는 것
- Render Web Service + Cron Job 배포
- KIS로 국내 종목 현재가 조회
- Yahoo Finance로 미국 종목 현재가/뉴스 조회
- Naver News 조회
- Gemini로 뉴스 요약/감성 점수 생성
- Telegram으로 점심/저녁 리포트 발송

## 아직 안 넣은 것
- 기존 Apps Script의 모든 점수 로직 이식
- Google Sheets 양방향 동기화
- POSITION / ENTRY_ALERTS 완전 이식
- 백테스트 / 성과대시보드

즉, 이건 **1차 서버 이전 시작점**입니다.

## 폴더 구조
```text
app/
  clients/   외부 API 클라이언트
  core/      설정, 로깅
  models/    데이터 구조
  services/  워치리스트, 점수, 리포트 엔진
  jobs.py    Render Cron 진입점
  main.py    FastAPI 진입점
```

## 로컬 실행
```bash
python -m venv .venv
source .venv/bin/activate   # Windows는 .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.jobs manual
```

## Render 배포
1. GitHub에 업로드
2. Render에서 `Blueprint` 또는 `New +`로 연결
3. 환경변수 입력
4. Cron Job 2개 확인
   - lunch: `python -m app.jobs lunch`
   - evening: `python -m app.jobs evening`

## 최소 환경변수
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- GEMINI_API_KEY
- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET
- KIS_APP_KEY
- KIS_APP_SECRET

## 시작 팁
처음에는 `watchlist.sample.json`을 3~4개 종목만 남기세요.

## 다음 이식 추천 순서
1. Google Sheets WATCHLIST 읽기
2. ENTRY_ALERTS 서버 생성
3. 기존 Apps Script 점수 로직 이식
4. POSITION 모니터링/익절/손절 서버 이전
