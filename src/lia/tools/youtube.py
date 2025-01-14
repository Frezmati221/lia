from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import lia.clients.client_youtube as client_youtube
class YoutubeUploadToolInput(BaseModel):
    """Input schema for YoutubeUploadTool."""
    file: str = Field(..., description="Name of the file to upload.")

class YoutubeUploadTool(BaseTool):
    name: str = "YoutubeUploadTool"
    description: str = (
        "A tool that can be used to upload a video to YouTube."
    )
    args_schema: Type[BaseModel] = YoutubeUploadToolInput

    def _run(self, file: str) -> str:
        return client_youtube.upload_video(file)
