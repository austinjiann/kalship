from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class VideoJobRequest:
    """Request to create a video job"""
    title: str
    caption: str
    bet: Optional[dict] = None
    duration_seconds: int = 6


@dataclass
class WorkerJobPayload:
    """Payload sent to worker for processing"""
    job_id: str
    title: str
    caption: str
    bet: Optional[dict] = None
    duration_seconds: int = 6


@dataclass
class JobStatus:
    status: Optional[Literal["done", "waiting", "error"]]
    job_start_time: Optional[datetime] = None
    job_end_time: Optional[datetime] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    bet: Optional[dict] = None
