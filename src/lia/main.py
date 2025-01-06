#!/usr/bin/env python
import sys
import warnings
from loguru import logger
from lia.crews.twitter_crew import Lia
from lia.crews.video_generate_crew import VideoGenerateCrew
from lia.characters.lia import characterLia
import lia.clients.client_twitter_off as client_twitter
import signal
import sys
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from lia.admin.app import app as admin_panel
import os
import dotenv
from lia.crews.twitter_actions import LiaTwitterActions
dotenv.load_dotenv()
# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


# def signal_handler(sig, frame):
#     print('Exiting...')
#     cleanup()
#     sys.exit(0)

# def cleanup():
#     print('Logging out from twitter')
#     client_twitter.logout()

# # Set up the signal handler
# print("Setting up signal handler for SIGINT...")
# signal.signal(signal.SIGINT, signal_handler)


def run():
    logger.info('Starting admin panel')
    admin_panel.run(host='0.0.0.0', port=1234)
    # VideoGenerateCrew().crew().kickoff(inputs={})
    # inputs = {
    #     'style': characterLia['style'],
    #     'domain': characterLia['topics'],
    #     'knowledge': characterLia['knowledge'],
    #     'agentName': characterLia['name'],
    #     'twitterUserName': characterLia['twitterUserName'],
    #     'bio': characterLia['bio'],
    #     'lore': characterLia['lore'],
    #     'topics': characterLia['topics'],
    #     'characterPostExamples': characterLia['characterPostExamples'],
    #     'adjectives': characterLia['adjectives'],
    #     'maxTweetLength': 280,
    # }
    # LiaTwitterActions().crew().kickoff(inputs=inputs)
    # VideoGenerateCrew().crew().kickoff(inputs={})
    
    """
    Run the crew.
    """
    # inputs = {
    #     'style': characterLia['style'],
    #     'domain': characterLia['topics'],
    #     'knowledge': characterLia['knowledge'],
    #     'agentName': characterLia['name'],
    #     'twitterUserName': characterLia['twitterUserName'],
    #     'bio': characterLia['bio'],
    #     'lore': characterLia['lore'],
    #     'topics': characterLia['topics'],
    #     'characterPostExamples': characterLia['characterPostExamples'],
    #     'adjectives': characterLia['adjectives'],
    #     'maxTweetLength': 280,
    # }
    # Lia().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Lia().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Lia().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Lia().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
