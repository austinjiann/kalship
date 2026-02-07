# QHacks - YouTube Shorts x Kalshi Prediction Markets

## Overview

TikTok-style feed pairing YouTube Shorts with Kalshi prediction market bets. Users scroll shorts, see matched bets, and queue Veo-generated bet explainer videos.

## Status

### Implemented
- [x] Kalshi API integration with RSA auth
- [x] YouTube metadata fetching
- [x] GPT keyword extraction from video title/description
- [x] GPT market matching (keywords → best Kalshi bet)
- [x] Frontend feed with auto-loading bets
- [x] YouTube Shorts embed with autoplay (muted)

### TODO
- [ ] Veo video generation for bet explainers
- [ ] Database caching for pre-computed matches

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  page.tsx → fetches /feed on load → shows loading spinner        │
│  Feed.tsx → scrollable container with snap scrolling             │
│  ShortCard.tsx → YouTube iframe embed (muted autoplay)           │
│  Bet overlay → shows matched Kalshi market with YES/NO prices    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (BlackSheep)                        │
│  GET /feed          → Pre-matched shorts + bets                  │
│  GET /match?video_id → Match single video to bet                 │
│  GET /markets       → Raw Kalshi markets                         │
│  POST /generate     → Queue Veo video (not implemented)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Services Layer                            │
│  KalshiService     → RSA auth, fetch markets, GPT matching       │
│  VideoAnalysis     → YouTube API metadata, GPT keyword extraction│
│  MatchingService   → Orchestrate video → market matching         │
└─────────────────────────────────────────────────────────────────┘
```

## Video-to-Bet Matching Flow (Current)

```
YouTube Short (video_id)
    ↓
YouTube API → title + description + channel
    ↓
GPT-4o → Extract 3-5 keywords (sports, politics, crypto, weather)
    ↓
Kalshi API → Fetch 100 open markets
    ↓
GPT-4o → Rank markets by relevance to keywords
    ↓
Return Best Match: { ticker, title, yes_price, no_price, volume }
```

## Kalshi API Authentication

- Base: `https://api.elections.kalshi.com/trade-api/v2`
- Sign: `{timestamp_ms}{METHOD}/trade-api/v2{path}` with RSA-PSS + SHA256
- Headers: `KALSHI-ACCESS-KEY`, `KALSHI-ACCESS-SIGNATURE`, `KALSHI-ACCESS-TIMESTAMP`

## Market Response Fields

| Field | Description |
|-------|-------------|
| `ticker` | Market identifier (e.g., `KXBTC-25000`) |
| `yes_sub_title` | Human-readable title |
| `yes_bid` | YES price (0-100 cents) |
| `no_bid` | NO price (0-100 cents) |
| `volume` | Trading volume |

## Backend Services

### KalshiService (`backend/services/kalshi_service.py`)
- `get_markets(status, limit)` - Fetch open markets via aiohttp
- `search_markets_by_keywords(keywords)` - GPT-powered matching

### VideoAnalysisService (`backend/services/video_analysis_service.py`)
- `get_video_metadata(video_id)` - YouTube Data API
- `extract_keywords(title, description)` - GPT extracts 3-5 keywords
- `analyze_video(video_id)` - Orchestrates metadata + keywords

### MatchingService (`backend/services/matching_service.py`)
- `match_video_to_market(video_id)` - Full pipeline
- `match_videos_batch(video_ids)` - Batch processing for /feed

## API Endpoints

| Endpoint | Description | Status |
|----------|-------------|--------|
| `GET /feed?limit=20` | Pre-matched shorts + bets | ✅ |
| `GET /match?video_id=` | Match single video | ✅ |
| `GET /markets?limit=100` | Raw Kalshi markets | ✅ |
| `POST /generate` | Queue Veo video | ❌ |

## Environment Variables

```
KALSHI_API_KEY=
KALSHI_PRIVATE_KEY_PATH=./kalshi_private_key.pem
OPENAI_API_KEY=
YOUTUBE_API_KEY=
GOOGLE_CLOUD_PROJECT=
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

## Dependencies

- `aiohttp` - Async HTTP client (using instead of httpx due to Python 3.14 SSL issues)
- `cryptography` - RSA signing for Kalshi auth
- `openai` - GPT-4o for keyword extraction and market matching
- `yt-dlp` - Video/audio download
- `blacksheep` - Python async web framework
- `pydantic-settings` - Environment variable management
