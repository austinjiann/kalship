from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class VideoJobRequest:
    starting_image: bytes
    custom_prompt: Optional[str] = None
    global_context: Optional[str] = None
    ending_image: Optional[bytes] = None
    duration_seconds: int = 6


@dataclass
class JobStatus:
    status: Optional[Literal["done", "waiting", "error"]]
    job_start_time: Optional[datetime] = None
    job_end_time: Optional[datetime] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None