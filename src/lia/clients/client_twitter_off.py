import os
from requests_oauthlib import OAuth1Session
import dotenv
import yaml
from urllib.parse import quote


dotenv.load_dotenv()

CLIENT_KEY = os.getenv('CLIENT_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:1234/twitter/callback'

def load_tokens():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    access_token = config.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = config.get('TWITTER_ACCESS_TOKEN_SECRET')
    if access_token and access_token_secret:
        return access_token, access_token_secret
    return None, None

# Save tokens to .env
def save_tokens(access_token, access_token_secret):
    config_file = 'config.yaml'
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        config = {}

    config['TWITTER_ACCESS_TOKEN'] = access_token
    config['TWITTER_ACCESS_TOKEN_SECRET'] = access_token_secret

    with open(config_file, 'w') as f:
        yaml.safe_dump(config, f)

def login():
    access_token, access_token_secret = load_tokens()

    if access_token and access_token_secret:
        print("Using saved access tokens from environment.")
        oauth_session = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET,
                                      resource_owner_key=access_token,
                                      resource_owner_secret=access_token_secret)
        return oauth_session

    request_token_url = 'https://api.twitter.com/oauth/request_token'
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri=REDIRECT_URI)
    response = oauth.post(request_token_url)

    if response.status_code == 200:
        credentials = dict([x.split('=') for x in response.text.split('&')])
        oauth_token = credentials.get('oauth_token')
        oauth_token_secret = credentials.get('oauth_token_secret')
        authorization_url = f"https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}"
        return authorization_url, oauth_token, oauth_token_secret

    else:
        raise Exception('Error obtaining request token: ' + response.text)\
        

def get_authenticated_user_id():

    url = "https://api.twitter.com/2/users/me" 
    
    try:
        response = oauth_session.get(url)
        response.raise_for_status()
        user_data = response.json()
        return user_data["data"]["id"]
    except Exception as e:
        print(f"Error retrieving authenticated user ID: {e}")
        return None


with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def create_post(text):
    if os.getenv('state') != 'prod':
        print("Not in prod mode, skipping tweet posting")
        return {"status": "success", "message": "Tweet posted successfully"}
    if not oauth_session:
        raise Exception("OAuth session is not initialized.")

    post_url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}
    
    response = oauth_session.post(post_url, json=payload)

    if response.status_code in [200, 201]:
        print("\n" + "=" * 30)
        print("Successfully posted the tweet!")
        print("=" * 30 + "\n")
        return {"status": "success", "message": "Tweet posted successfully"}
    else:
        print("\n" + "=" * 30)
        print("=" * 30 + "\n")
        return {"status": "error", "message": response}
    

def search_tweets(query):

    if os.getenv('state') != 'prod':
        print("Not in prod mode, skipping tweet searching")
        return {
            "data": [
                {
                "id": "1373001119480344583",
                "edit_history_tweet_ids": [
                    "1373001119480344583"
                ],
                "text": "Looking to get started with the Twitter API but new to APIs in general? @jessicagarson will walk you through everything you need to know in APIs 101 session. She’ll use examples using our v2 endpoints, Tuesday, March 23rd at 1 pm EST.nnJoin us on Twitchnhttps://t.co/GrtBOXyHmB"
                },
                {
                "id": "1372627771717869568",
                "edit_history_tweet_ids": [
                    "1372627771717869568"
                ],
                "text": "Thanks to everyone who joined and made today a great session! 🙌 nnIf weren't able to attend, we've got you covered. Academic researchers can now sign up for office hours for help using the new product track. See how you can sign up, here 👇nhttps://t.co/duIkd27lPx https://t.co/AP9YY4F8FG"
                },
                {
                "id": "1367519323925843968",
                "edit_history_tweet_ids": [
                    "1367519323925843968"
                ],
                "text": "Meet Aviary, a modern client for iOS 14 built using the new Twitter API. It has a beautiful UI and great widgets to keep you up to date with the latest Tweets. https://t.co/95cbd253jK"
                },
                {
                "id": "1366832168333234177",
                "edit_history_tweet_ids": [
                    "1366832168333234177"
                ],
                "text": "The new #TwitterAPI provides the ability to build the Tweet payload with the fields that you want. nnIn this tutorial @suhemparack explains how to build the new Tweet payload and how it compares with the old Tweet payload in v1.1 👇 https://t.co/eQZulq4Ik3"
                },
                {
                "id": "1364984313154916352",
                "edit_history_tweet_ids": [
                    "1364984313154916352"
                ],
                "text": "“I was heading to a design conference in New York and wanted to meet new people,” recalls @aaronykng, creator of @flocknet. “There wasn't an easy way to see all of the designers in my network, so I built one.” Making things like this opened the doors for him to the tech industry."
                },
                {
                "id": "1364275610764201984",
                "edit_history_tweet_ids": [
                    "1364275610764201984"
                ],
                "text": "If you're newly approved for the Academic Research product track, our next stream is for you.nnThis Thursday, February 25th at 10AM PST @suhemparack will demo how academics can use this track to get started with the new #TwitterAPInnJoin us on Twitch! 👀nhttps://t.co/SQziibOD9P"
                }
            ],
            "meta": {
                "newest_id": "1373001119480344583",
                "oldest_id": "1364275610764201984",
                "result_count": 6
                        }
                    }
    if not oauth_session:
        raise Exception("OAuth session is not initialized.")
    encoded_query = quote(query).lower()
    response = oauth_session.get(
        f"https://api.twitter.com/2/tweets/search/recent?query={encoded_query}&tweet.fields=public_metrics,conversation_id&sort_order=relevancy"
    )
    return response.json()

def retweet_post(tweet_id):

    if os.getenv('state') != 'prod':
        print("Not in prod mode, skipping retweet posting.")
        return {
            "status": "success",
            "message": "Retweet mocked successfully",
            "tweet_id": tweet_id
        }

    if not oauth_session:
        raise Exception("OAuth session is not initialized.")

    url = f"https://api.twitter.com/2/users/{user_id}/retweets"

    payload = {
        "tweet_id": tweet_id
    }

    try:
        response = oauth_session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error during retweet: {e}")
        return {
            "status": "error",
            "message": str(e),
            "tweet_id": tweet_id
        }


def post_comment(tweet_id, comment_text):
    if os.getenv('state') != 'prod':
        print("Not in prod mode, skipping comment posting")
        return {
            "status": "success",
            "message": "Comment mocked successfully",
            "tweet_id": tweet_id,
            "comment_text": comment_text
        }

    if not oauth_session:
        raise Exception("OAuth session is not initialized.")

    url = "https://api.twitter.com/2/tweets"

    payload = {
        "text": comment_text,
        "in_reply_to_tweet_id": tweet_id
    }

    response = oauth_session.post(url, json=payload)

    response.raise_for_status()

    return response.json()




if os.getenv('state') == 'prod' and (config.get('TWITTER_ACCESS_TOKEN') and config.get('TWITTER_ACCESS_TOKEN_SECRET')):
    oauth_session = None
    oauth_session = login()
    user_id = get_authenticated_user_id()
    print(user_id)
    print("logged in")
else:
    print("testing mode")
