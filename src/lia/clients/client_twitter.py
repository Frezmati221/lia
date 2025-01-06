import asyncio
from typing import Literal
from twikit import Client
import os
from dotenv import load_dotenv
import json
from loguru import logger

load_dotenv(dotenv_path='../.env')

USERNAME = os.getenv('TWITTER_USERNAME')
EMAIL = os.getenv('TWITTER_EMAIL')
PASSWORD = os.getenv('TWITTER_PASSWORD')
PATH_TO_COOKIES = os.getenv('PATH_TO_TWITTER_COOKIES')
PROXYURL = os.getenv('PROXYURL')
client = Client('en-US', proxy=PROXYURL)

async def login():
    if not os.path.exists(f'{PATH_TO_COOKIES}/twitter_account_cookie'):
        logger.info('Logging in with credentials to twitter')
        try:    
            login = await client.login(
                auth_info_1=USERNAME,
                auth_info_2=EMAIL,
                password=PASSWORD
            )
            logger.info('Saving cookies')
            twitter_cookies = client.get_cookies()
            with open(f'{PATH_TO_COOKIES}/twitter_account_cookie', 'w') as cookie_file:
                json.dump(twitter_cookies, cookie_file)
        except Exception as e:
            logger.error(f'Error logging in: {e}')
            return
    else: 
        logger.info('Using cookies to login')
        with open(f'{PATH_TO_COOKIES}/twitter_account_cookie', 'r') as cookie_file:
            twitter_cookies = json.load(cookie_file)
            client.set_cookies(twitter_cookies)
            logger.info("Logged in with cookies")
        logger.success(f'Logged in as {USERNAME}')






async def logout():
    try:
        logger.info('Logging out from twitter')
        await client.logout()
    except Exception as e:
        logger.error(f'Error logging out: {e}')
        return
    
async def create_tweet(text: str = '', media_ids: list[str] | None = None, poll_uri: str | None = None, reply_to: str | None = None, conversation_control: Literal['followers', 'verified', 'mentioned'] | None = None, attachment_url: str | None = None, community_id: str | None = None, share_with_followers: bool = False, is_note_tweet: bool = False, richtext_options: list[dict] = None, edit_tweet_id: str | None = None):
    try:
        logger.info(f'Posting tweet: {text}')
        await client.create_tweet(text, media_ids, poll_uri, reply_to, conversation_control, attachment_url, community_id, share_with_followers, is_note_tweet, richtext_options, edit_tweet_id)
    except Exception as e:
        logger.error(f'Error posting tweet: {e}')
        return
    
async def test(text: str):
    logger.info(text)
    print(text)

async def search_tweets(query: str, product: Literal['Top', 'Latest', 'Popular'], count: int = 25, cursor: str | None = None):
    try:
        logger.info(f'Searching {count} tweets')
        tweets = await client.search_tweet(query, product, count, cursor)
        tweet_list = []
        
        for tweet in tweets:
            tweet_data = {
                'id': tweet.id,
                'text': tweet.text,
                'likes': tweet.favorite_count,
                'views': tweet.view_count,
                'retweets': tweet.retweet_count,
                'replies': tweet.reply_count,
            }
            tweet_list.append(tweet_data)

        return tweet_list

    except Exception as e:
        logger.error(f'Error searching tweets: {e}')
        return []
    

async def get_trends(category: Literal['trending', 'for-you', 'news', 'sports', 'entertainment'], count: int = 20, retry: bool = True, additional_request_params: dict | None = None): 
    try:
        logger.info('Getting trends')
        trends = await client.get_trends(category, count, retry, additional_request_params)
        return trends
    except Exception as e:
        logger.error(f'Error getting trends: {e}')
        return
    

async def retweet(tweet_id: str):
    try:
        logger.info(f'Retweeting tweet: {tweet_id}')
        await client.retweet(tweet_id)
    except Exception as e:
        logger.error(f'Error retweeting tweet: {e}')
        return
    

async def like_tweet(tweet_id: str):
    try:
        logger.info(f'Liking tweet: {tweet_id}')
        await client.favorite_tweet(tweet_id)
    except Exception as e:
        logger.error(f'Error liking tweet: {e}')
        return


async def follow_user(user_id: str):
    try:
        logger.info(f'Following user: {user_id}')
        await client.follow_user(user_id)
    except Exception as e:
        logger.error(f'Error following user: {e}')
        return
    

if os.getenv('state') == 'prod':
    asyncio.run(login())