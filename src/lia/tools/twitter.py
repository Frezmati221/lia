from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import lia.clients.client_twitter_off as client_twitter
import lia.clients.client_twitter as client_twitter_with_proxy
import asyncio
class PostTweetToolInput(BaseModel):
    """Input schema for PostTweetTool."""
    text: str = Field(..., description="Text of the tweet.")

class PostTweetTool(BaseTool):
    name: str = "PostTweetTool"
    description: str = (
        "A tool that can be used to post tweet to twitter with a text."
    )
    args_schema: Type[BaseModel] = PostTweetToolInput

    def _run(self, text: str) -> str:
        return client_twitter.create_post(text)


class SearchTweetsToolInput(BaseModel):
    """Input schema for SearchTweetsTool."""
    query: str = Field(..., description="Query to search for tweets.")


class SearchTweetsTool(BaseTool):
    name: str = "SearchTweetsTool"
    description: str = (
        "A tool that can be used to search tweets from twitter."
    )
    args_schema: Type[BaseModel] = SearchTweetsToolInput

    def _run(self, query: str) -> str:
        return asyncio.run(client_twitter_with_proxy.search_tweets(query, 'Top'))

class RetweetPostToolInput(BaseModel):
    tweet_id: str = Field(..., description="Id of the tweet to retweet.")

class RetweetPostTool(BaseTool):
    name: str = "RetweetPostTool"
    description: str = (
        "A tool that can be used to retweet a tweet."
    )
    args_schema: Type[BaseModel] = RetweetPostToolInput
    def _run(self, tweet_id: str) -> str:
        return client_twitter.retweet_post(tweet_id)
    
class QuotePostToolInput(BaseModel):
    tweet_id: str = Field(..., description="Id of the tweet to quote.")
    comment_text: str = Field(..., description="Text of the comment to add to the tweet.")
    
class QuotePostTool(BaseTool):
    name: str = "QuotePostTool"
    description: str = (
        "A tool that can be used to quote a tweet."
    )
    args_schema: Type[BaseModel] = QuotePostToolInput
    def _run(self, tweet_id: str, comment_text: str) -> str:
        return client_twitter.post_comment(tweet_id, comment_text)
    