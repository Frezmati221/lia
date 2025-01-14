from crewai.tools import BaseTool
from typing import Type
import cv2
import numpy as np
from pydantic import BaseModel, Field
from datetime import datetime
import json
import requests
from crewai.tools import BaseTool
from openai import OpenAI

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


class ImagePromptSchema(BaseModel):
    """Input for Dall-E Tool."""

    description: str = "Description of the image to be generated."


class ImageTool(BaseTool):
    name: str = "ImageTool"
    description: str = "Generates images with a given description."
    args_schema: Type[BaseModel] = ImagePromptSchema

    model: str = "dall-e-3"
    size: str = "1024x1024"
    quality: str = "standard"
    n: int = 1

    def _run(self, description: str) -> str:
        client = OpenAI()
        

        response = client.images.generate(
            model=self.model,
            prompt=description,
            size=self.size,
            quality=self.quality,
            n=self.n,
        )

        image_data = json.dumps(
            {
                "image_url": response.data[0].url,
                "image_description": response.data[0].revised_prompt,
            }
        )

        return image_data
    

class ImageSearchToolInput(BaseModel):
    """Input for ImageSearchTool."""

    description: str = "Exact terms of the image to be found in the internet. Not more than 5 words. It is using strict search by words. Make description very carefully."

class ImageSearchTool(BaseTool):
    name: str = "ImageSearchTool"
    description: str = "Searches for images in the internet."
    args_schema: Type[BaseModel] = ImageSearchToolInput
    
     
    def _run(self, description: str) -> str:
        params = {
            "key": "AIzaSyAdT8ikNkXYFacnLcHNxfEvVDGky8lwv5U",
            "cx": "74d8d375e737a4f43",
            "q": description,
            "searchType": "image",
            "num": 1,
            "safe": "active"
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()

            results = response.json()
            image_urls = [item["link"] for item in results.get("items", [])]
            return image_urls
        except Exception as e:
            print(f"Error during image search: {e}")
            return []


class FetchImageToolInput(BaseModel):
    """Input for FetchImageTool."""

    url: str = "URL of the image to be fetched."

class FetchImageTool(BaseTool):
    name: str = "FetchImageTool"
    description: str = "Fetches an image from the internet."
    args_schema: Type[BaseModel] = FetchImageToolInput

    def _run(self, url: str) -> str:
        """Fetch image from URL and return it as a numpy array."""
        response = requests.get(url)
        if response.status_code == 200:
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:  # Check if the image is valid
                return {"Image fetched successfully"}
            else:
                return {"Failed to decode image from the fetched content."}
        else:
            return {"Failed to fetch image from {url}"}
