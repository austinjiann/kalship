from blacksheep import Application
from rodi import Container

from services.test_service import TestService
from services.feed_service import FeedService
from services.job_service import JobService
from services.vertex_service import VertexService

services = Container()
services.add_scoped(TestService)
services.add_scoped(FeedService)
services.add_scoped(VertexService)
services.add_scoped(JobService)

app = Application(services=services)

app.use_cors(
    allow_methods="*",
    allow_origins="*",
    allow_headers="*",
)