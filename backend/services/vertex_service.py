from google import genai
from google.genai.types import (
    GenerateVideosConfig,
    GenerateVideosOperation,
    Image,
    GenerateContentConfig,
    ImageConfig,
    Part,
)
from models.job import JobStatus
from utils.env import settings

class VertexService:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        self.bucket_name = settings.GOOGLE_CLOUD_BUCKET_NAME

    async def generate_video_content(self, prompt: str, image_data: bytes = None, ending_image_data: bytes = None, duration_seconds: int = 6) -> GenerateVideosOperation:
        ending_frame = None
        if ending_image_data:
            ending_frame = Image(
                image_bytes=ending_image_data,
                mime_type="image/png",
            )

        # gen vid
        operation = self.client.models.generate_videos(
            model="veo-3.1-fast-generate-001",
            prompt=prompt,
            image=Image(
                image_bytes=image_data,
                mime_type="image/png",
            ),
            config=GenerateVideosConfig(
                aspect_ratio="16:9",
                duration_seconds=duration_seconds,
                output_gcs_uri=f"gs://{self.bucket_name}/videos/",
                negative_prompt="text, captions, subtitles, annotations, low quality, static, ugly, weird physics",
                last_frame=ending_frame,
            ),
        )

        return operation
    
    async def generate_image_from_prompt(
        self,
        prompt: str,
        image: bytes | None = None,
    ) -> bytes:
        if not prompt:
            raise ValueError("prompt is required")

        if image:
            # Image-to-image
            contents = [
                Part.from_bytes(data=image, mime_type="image/png"),
                prompt,
            ]
        else:
            # Text-to-image
            contents = [prompt]

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=contents,
            config=GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=ImageConfig(
                    aspect_ratio="16:9",
                ),
                candidate_count=1,
            ),
        )
        if not response.candidates or not response.candidates[0].content.parts:
            raise Exception(str(response))
        return response.candidates[0].content.parts[0].inline_data.data

    async def generate_image_content(
        self,
        title: str,
        caption: str,
        additional: str | None = None,
        image: bytes | None = None
    ) -> bytes:
        prompt = f"{title}\n{caption}"
        if additional:
            prompt += f"\n{additional}"
        return await self.generate_image_from_prompt(prompt=prompt, image=image)
    
    async def get_video_status(self, operation: GenerateVideosOperation) -> JobStatus:
        operation = self.client.operations.get(operation)
        if operation.done and operation.result and operation.result.generated_videos:
            return JobStatus(status="done", job_start_time=None, video_url=operation.result.generated_videos[0].video.uri)
        return JobStatus(status="waiting", job_start_time=None, video_url=None)
    
    async def get_video_status_by_name(self, operation_name: str) -> JobStatus:
        """Get video status by operation name (avoids serialization)"""
        # Create a minimal operation object with just the name since get() expects an operation object
        operation = GenerateVideosOperation(name=operation_name)
        operation = self.client.operations.get(operation)
        if operation.done and operation.result and operation.result.generated_videos:
            return JobStatus(status="done", job_start_time=None, video_url=operation.result.generated_videos[0].video.uri)
        return JobStatus(status="waiting", job_start_time=None, video_url=None)
