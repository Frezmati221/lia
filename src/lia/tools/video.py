from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import lia.clients.client_video as client_video
import asyncio
import json
class VideoToolInput(BaseModel):
    """Input schema for VideoTool."""
    xml_data: str = Field(..., description="XML text that will be used to make a video.")

class MakeVideoTool(BaseTool):
    name: str = "MakeVideoTool"
    description: str = (
        "A tool that can be used to make a video from a XML file."
    )
    args_schema: Type[BaseModel] = VideoToolInput

    def _run(self, xml_data: str) -> str:
        return client_video.make_video(xml_data)

