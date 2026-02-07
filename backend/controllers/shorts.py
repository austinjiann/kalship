# yt shorts fetching logic

from blacksheep import json
from blacksheep.server.controllers import APIController, get, post
from services.test_service import TestService

class Shorts(APIController):
    def __init__(self, test_service: TestService):
        self.test_service = test_service

    @get("/health")
    async def health_check(self):
        return json({"status": "ok"})

# call klashi functions