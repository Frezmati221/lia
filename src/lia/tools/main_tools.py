from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime

class TimeToolInput(BaseModel):
    """Input schema for TimeTool."""

class TimeTool(BaseTool):
    name: str = "TimeTool"
    description: str = (
        "A tool that can be used to get the current time."
    )
    args_schema: Type[BaseModel] = TimeToolInput

    def _run(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

