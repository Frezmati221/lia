#!/usr/bin/env python
import sys
import warnings
from loguru import logger
from lia.crews.twitter_crew import Lia
from lia.crews.video_generate_crew import VideoGenerateCrew
from lia.crews.svideo_crew import SVideoCrew
from lia.characters.lia import characterLia
import lia.clients.client_twitter_off as client_twitter
import signal
import sys
import re
import os
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from lia.admin.app import app as admin_panel
import dotenv
from lia.crews.twitter_actions import LiaTwitterActions
from lia.clients.client_youtube import upload_video
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
    # upload_video("svideo/video.mp4")
    # logger.info('Starting admin panel')

    admin_panel.run(debug=True, host='0.0.0.0', port=1234)
    
    # log_dir = os.getenv('VIDEO_EXCLUDE_TOPICS_PATH') + "/"
    # base_filename = 'svideo_exclude_topic'
    # extension = '.txt'
    
    # existing_files = os.listdir(log_dir)
    # matching_files = [
    #     f for f in existing_files 
    #     if re.match(rf"{base_filename}_(\d+){extension}", f)
    # ]
    
    # combined_file_path = os.path.join(log_dir, f"{base_filename}_combined{extension}")
    
    # exclude_topics_content = ""
    # if os.path.exists(combined_file_path):
    #     with open(combined_file_path, 'r') as combined_file:
    #         exclude_topics_content = combined_file.read()
    
    # if matching_files:
    #     for file_name in matching_files:
    #         with open(os.path.join(log_dir, file_name), 'r') as file:
    #             exclude_topics_content += file.read() + "\n"
        
    #     # Write the updated content back to the combined file
    #     with open(combined_file_path, 'w') as combined_file:
    #         combined_file.write(exclude_topics_content)
        
    #     for file_name in matching_files:
    #         os.remove(os.path.join(log_dir, file_name))
    
    # SVideoCrew().crew().kickoff(inputs={
    #     'domain': 'history,world,science,technology,art,literature,music,philosophy,religion,culture,sports,controvertial theories, mysteries, and conspiracies, myths, legends, and folklore.',
    #     'exclude_topics': exclude_topics_content
    # })
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
