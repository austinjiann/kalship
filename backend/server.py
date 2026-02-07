from blacksheep import Application, Request, json
from services.test_service import TestService
from services.matching_service import MatchingService
from services.kalshi_service import KalshiService
from services.video_analysis_service import VideoAnalysisService
from rodi import Container

services = Container()

test_service = TestService()
matching_service = MatchingService()
kalshi_service = KalshiService()
video_analysis_service = VideoAnalysisService()

services.add_instance(test_service, TestService)
services.add_instance(matching_service, MatchingService)
services.add_instance(kalshi_service, KalshiService)

app = Application(services=services)

app.use_cors(
    allow_methods="*",
    allow_origins="*",
    allow_headers="*",
)

HARDCODED_VIDEO_IDS = [
    "vHaPgrSMlI0",
    "HZOkwNsYFdo",
    "w1rbnM6A4AA",
    "_qW6a1A9gb0",
    "3fQhDJlRJYg",
    "LQ8uCvKYu3Y",
]

@app.router.get("/")
def hello_world():
    return "Hello World"


@app.router.get("/test")
async def test_route():
    return await test_service.get_greeting("hello this works")


def get_query_param(request: Request, key: str, default: str) -> str:
    values = request.query.get(key)
    if values:
        return values[0].decode() if isinstance(values[0], bytes) else values[0]
    return default


@app.router.get("/match")
async def match_video(request: Request):
    video_id = get_query_param(request, "video_id", "")
    if not video_id:
        return json({"error": "video_id required"}, status=400)
    result = await matching_service.match_video_to_market(video_id)
    if not result:
        return json({"error": "No matching market found"}, status=404)
    return json(result)


@app.router.get("/feed")
async def get_feed(request: Request):
    limit = int(get_query_param(request, "limit", "20"))
    video_ids = HARDCODED_VIDEO_IDS[:limit]
    results = await matching_service.match_videos_batch(video_ids)
    feed = []
    for i, item in enumerate(results):
        feed.append({
            "id": str(i + 1),
            "youtube": item["youtube"],
            "kalshi": item["kalshi"],
        })
    return json(feed)


@app.router.get("/markets")
async def get_markets(request: Request):
    limit = int(get_query_param(request, "limit", "100"))
    status = get_query_param(request, "status", "open")
    result = await kalshi_service.get_markets(status=status, limit=limit)
    return json(result)


@app.router.get("/analyze")
async def analyze_video(request: Request):
    video_id = get_query_param(request, "video_id", "vHaPgrSMlI0")
    result = await video_analysis_service.analyze_video(video_id)
    return json(result)