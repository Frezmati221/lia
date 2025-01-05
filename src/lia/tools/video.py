from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import lia.clients.client_video as client_video
import asyncio
class VideoToolInput(BaseModel):
    """Input schema for VideoTool."""
    json_data: dict = Field(..., description="JSON file describing the plot.")

class MakeVideoTool(BaseTool):
    name: str = "MakeVideoTool"
    description: str = (
        "A tool that can be used to make a video from a JSON file."
    )
    args_schema: Type[BaseModel] = VideoToolInput

    def _run(self, json_data: str) -> str:
        return asyncio.run(client_video.make_video(json_data))

