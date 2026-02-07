from google import genai
from google.genai.types import GenerateVideosConfig, GenerateVideosOperation, Image, GenerateContentConfig, ImageConfig, Part, VideoGenerationReferenceImage
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

    async def analyze_image_content(self, prompt: str, image_data: bytes) -> str:
        """Analyze image and return text description"""
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                Part.from_bytes(data=image_data, mime_type="image/png"),
                prompt
            ]
        )
        return response.candidates[0].content.parts[0].text.strip()

    async def creative_director(self, context: str) -> dict:
        """
        Takes video/short context and generates creative prompts for video generation.
        Returns JSON with veo_prompt, start_frame_prompt, end_frame_prompt.
        """
        system_prompt = """You are a creative director for AI video generation.
Given context about a short video, generate three prompts:

1. veo_prompt: The main video generation prompt describing the action, movement, and mood
2. start_frame_prompt: Description of the opening frame/scene
3. end_frame_prompt: Description of the closing frame/scene

Respond ONLY with valid JSON in this exact format:
{
    "veo_prompt": "...",
    "start_frame_prompt": "...",
    "end_frame_prompt": "..."
}

Make prompts vivid, cinematic, and specific. Focus on visual details, lighting, camera angles, and emotion."""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[system_prompt, f"Context: {context}"],
        )

        import json
        text = response.candidates[0].content.parts[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)