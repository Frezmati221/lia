from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, session
import os
from lia.crews.twitter_crew import Lia
from lia.characters.lia import characterLia
import logging

from lia.crews.twitter_actions import LiaTwitterActions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv, set_key
from requests_oauthlib import OAuth1Session
from lia.clients.client_twitter_off import login as loginTwitter, save_tokens
from flask_cors import CORS
import random
import time
import threading
import yaml
load_dotenv()

# Example log
logger.info("Flask app started")
app = Flask(__name__)


app.secret_key = "secret" 




agents = [
    {"id": 1, "name": "Nova", "status": "waiting"},
    
]

logs = []


kickoff_initiated = False
actions_kickoff_initiated = False
start_time = None

waiting_time = None
actions_waiting_time = None

waiting_time_lock = threading.Lock()
actions_waiting_time_lock = threading.Lock()
# List to keep track of all active threads
active_threads = []

def decrement_waiting_time():
    global waiting_time
    while True:
        with waiting_time_lock:
            if waiting_time is not None and waiting_time > 0:
                waiting_time -= 1
        time.sleep(1)


def decrement_actions_waiting_time():
    global actions_waiting_time
    while True:
        with actions_waiting_time_lock:
            if actions_waiting_time is not None and actions_waiting_time > 0:
                actions_waiting_time -= 1
        time.sleep(1)

decrement_thread = threading.Thread(target=decrement_waiting_time, daemon=True)
decrement_actions_thread = threading.Thread(target=decrement_actions_waiting_time, daemon=True)

decrement_thread.start()
decrement_actions_thread.start()

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify({"agents": agents})

@app.route('/api/agents/<int:agent_id>/config', methods=['POST'])
def update_agent_config(agent_id):
    new_config = request.json
    for agent in agents:
        if agent['id'] == agent_id:
            agent.update(new_config)
            return jsonify({"success": True, "agent": agent})
    return jsonify({"error": "Agent not found"}), 404

@app.route('/api/kickoff', methods=['POST'])
def kickoff_crew():
    try:

        inputs = {
            'style': characterLia['style'],
            'domain': characterLia['topics'],
            'knowledge': characterLia['knowledge'],
            'agentName': characterLia['name'],
            'twitterUserName': characterLia['twitterUserName'],
            'bio': characterLia['bio'],
            'lore': characterLia['lore'],
            'topics': characterLia['topics'],
            'characterPostExamples': characterLia['characterPostExamples'],
            'adjectives': characterLia['adjectives'],
            'maxTweetLength': 280,
        }
        Lia().crew().kickoff(inputs=inputs)
        
        for agent in agents:
            agent['status'] = 'waiting'
        
        return jsonify({"success": True, "message": "Crew kickoff initiated successfully."})
    except Exception as e:
        for agent in agents:
            agent['status'] = 'waiting'
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/api/kickoff-actions', methods=['POST'])
def kickoff_actions():
    try:

        inputs = {
            'style': characterLia['style'],
            'domain': characterLia['topics'],
            'knowledge': characterLia['knowledge'],
            'agentName': characterLia['name'],
            'twitterUserName': characterLia['twitterUserName'],
            'bio': characterLia['bio'],
            'lore': characterLia['lore'],
            'topics': characterLia['topics'],
            'characterPostExamples': characterLia['characterPostExamples'],
            'adjectives': characterLia['adjectives'],
            'maxTweetLength': 280,
        }
        LiaTwitterActions().crew().kickoff(inputs=inputs)
        
        for agent in agents:
            agent['status'] = 'waiting'
        
        return jsonify({"success": True, "message": "Crew kickoff initiated successfully."})
    except Exception as e:
        for agent in agents:
            agent['status'] = 'waiting'
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/change-agent-status/<int:agent_id>/<status>', methods=['POST'])
def change_agent_status(agent_id, status):
    for agent in agents:
        if agent['id'] == agent_id:
            agent['status'] = status
            return jsonify({"success": True, "agent": agent})
    return jsonify({"error": "Agent not found"}), 404


@app.route('/login-status', methods=['GET'])
def login_status():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if config.get("TWITTER_ACCESS_TOKEN") and config.get("TWITTER_ACCESS_TOKEN_SECRET"):
        return jsonify({"loginRequired": False})
    else:
        return jsonify({"loginRequired": True})

@app.route('/')
def serve_index():
    return render_template('index.html', logs=logs)

@app.route('/twitter/login', methods=['GET'])
def twitter_login():
    try:
        authUrl, oauth_token, oauth_token_secret = loginTwitter()
        
        session['oauth_token'] = oauth_token
        session['oauth_token_secret'] = oauth_token_secret
        
        return jsonify({"success": True, "authUrl": authUrl})
    except Exception as e:
        logger.error(f"Error during Twitter login: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# New route to serve logs from the logs/twitter directory
@app.route('/logs')
def serve_logs():
    logs_directory = os.getenv("TWITTER_LOGS_PATH")
    log_files = sorted(
        os.listdir(logs_directory),
        key=lambda x: os.path.getctime(os.path.join(logs_directory, x)),
        reverse=True
    )
    logs_content = ""

    for log_file in log_files:
        with open(os.path.join(logs_directory, log_file), 'r') as file:
            logs_content += f"File: {log_file}\n{file.read()}\n"
    return logs_content

@app.route('/twitter/settings', methods=['GET'])
def serve_twitter_settings():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    twitter_settings = {
        "min_post_interval": config.get("TWITTER_POST_INTERVAL_MIN"),
        "max_post_interval": config.get("TWITTER_POST_INTERVAL_MAX"),
        "min_action_interval": config.get("TWITTER_ACTION_INTERVAL_MIN"),
        "max_action_interval": config.get("TWITTER_ACTION_INTERVAL_MAX"),
    }
    return jsonify(twitter_settings)


@app.route('/twitter/settings', methods=['POST'])
def update_settings():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Parse incoming JSON data
    data = request.json

    # Extract values for minInterval and maxInterval, ensure they are integers
    min_interval = data.get("minInterval")
    max_interval = data.get("maxInterval")
    action_min_interval = data.get("actionMinInterval")
    action_max_interval = data.get("actionMaxInterval")

    if not isinstance(min_interval, int) or not isinstance(max_interval, int):
        return jsonify({"success": False, "message": "minInterval and maxInterval must be integers"}), 400

    config["TWITTER_POST_INTERVAL_MIN"] = min_interval
    config["TWITTER_POST_INTERVAL_MAX"] = max_interval
    config["TWITTER_ACTION_INTERVAL_MIN"] = action_min_interval
    config["TWITTER_ACTION_INTERVAL_MAX"] = action_max_interval

    with open('config.yaml', 'w') as file:
        yaml.safe_dump(config, file)

    return jsonify({"success": True, "message": "Settings updated successfully."})

@app.route('/twitter/callback')
def twitter_callback():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    if not oauth_token or not oauth_verifier:
        return jsonify({"success": False, "message": "Missing oauth_token or oauth_verifier"}), 400

    try:
        oauth = OAuth1Session(os.getenv('CLIENT_KEY'), client_secret=os.getenv('CLIENT_SECRET'),
                              resource_owner_key=oauth_token,
                              verifier=oauth_verifier)
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens['oauth_token']
        access_token_secret = oauth_tokens['oauth_token_secret']

        save_tokens(access_token, access_token_secret)
        return redirect('/')
    except Exception as e:
        logger.error(f"Error during Twitter callback: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    




@app.route('/twitter/stop', methods=['POST'])
def stop_twitter_crew():
    global kickoff_initiated, start_time, waiting_time, actions_kickoff_initiated
    if not kickoff_initiated:
        return jsonify({"success": False, "message": "Crew is not running."}), 400
    if not actions_kickoff_initiated:
        return jsonify({"success": False, "message": "Actions crew is not running."}), 400
    elapsed_time = time.time() - start_time if start_time else 0
    print("\n" + "="*30)
    print("Stopping twitter crew...")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print("="*30 + "\n")
    kickoff_initiated = False
    actions_kickoff_initiated = False
    waiting_time = None
    start_time = None
    return jsonify({"success": True, "message": "Crew stopped.", "elapsedTime": elapsed_time})


@app.route('/twitter/actions', methods=['POST'])
def start_twitter_actions():
    global actions_kickoff_initiated, start_time, actions_waiting_time
    if actions_kickoff_initiated:
        return jsonify({"success": False, "message": "Actions crew is already running."}), 400

    actions_kickoff_initiated = True
    start_time = time.time()
    
    print("\n" + "="*30)
    print("Starting twitter actions crew...")
    print("="*30 + "\n")
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        min_interval = config.get("TWITTER_ACTION_INTERVAL_MIN", 100)
        max_interval = config.get("TWITTER_ACTION_INTERVAL_MAX", 300)
        interval = random.randint(min_interval, max_interval)
        print("\n" + "="*30)
        print(f"Initial wait for {interval*60} seconds before first kickoff actions.")
        print("="*30 + "\n")
        actions_waiting_time = interval*60
        print(f"actions_waiting_time set to {actions_waiting_time}")
        time.sleep(interval*60)

        while actions_kickoff_initiated and actions_waiting_time <= 1:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            inputs = {
                'style': characterLia['style'],
                'domain': characterLia['topics'],
                'knowledge': characterLia['knowledge'],
                'agentName': characterLia['name'],
                'twitterUserName': characterLia['twitterUserName'],
                'bio': characterLia['bio'],
                'lore': characterLia['lore'],
                'topics': characterLia['topics'],
                'characterPostExamples': characterLia['characterPostExamples'],
                'adjectives': characterLia['adjectives'],
                'maxTweetLength': 280,
            }
            LiaTwitterActions().crew().kickoff(inputs=inputs)
            
            min_interval = int(config.get("TWITTER_ACTION_INTERVAL_MIN", 100))
            max_interval = int(config.get("TWITTER_ACTION_INTERVAL_MAX", 300))
            interval = random.randint(min_interval, max_interval)
            actions_waiting_time = interval*60
            logger.info(f"Next actions_waiting_time set to {actions_waiting_time}")

            print(f"Next kickoff actions in {interval*60} seconds.")
            time.sleep(interval*60)
        
        return jsonify({"success": True, "message": "Crew kickoff actions started."})
    except Exception as e:
        actions_kickoff_initiated = False
        logger.error(f"Error during crew kickoff: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/twitter/start', methods=['POST'])
def start_twitter_crew():
  
    global kickoff_initiated, start_time, waiting_time
    if kickoff_initiated:
        return jsonify({"success": False, "message": "Crew is already running."}), 400

    kickoff_initiated = True
    start_time = time.time()
    
    print("\n" + "="*30)
    print("Starting twitter crew...")
    print("="*30 + "\n")

    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        min_interval = config.get("TWITTER_POST_INTERVAL_MIN", 100)
        max_interval = config.get("TWITTER_POST_INTERVAL_MAX", 300)
        interval = random.randint(min_interval, max_interval)
        print("\n" + "="*30)
        print(f"Initial wait for {interval*60} seconds before first kickoff.")
        print("="*30 + "\n")
        waiting_time = interval*60
        time.sleep(interval*60)


        while kickoff_initiated and waiting_time<=1:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            inputs = {
                'style': characterLia['style'],
                'domain': characterLia['topics'],
                'knowledge': characterLia['knowledge'],
                'agentName': characterLia['name'],
                'twitterUserName': characterLia['twitterUserName'],
                'bio': characterLia['bio'],
                'lore': characterLia['lore'],
                'topics': characterLia['topics'],
                'characterPostExamples': characterLia['characterPostExamples'],
                'adjectives': characterLia['adjectives'],
                'maxTweetLength': 280,
            }
            Lia().crew().kickoff(inputs=inputs)
            
            min_interval = int(config.get("TWITTER_POST_INTERVAL_MIN", 100))
            max_interval = int(config.get("TWITTER_POST_INTERVAL_MAX", 300))
            interval = random.randint(min_interval, max_interval)
            waiting_time = interval*60

            print(f"Next kickoff in {interval*60} seconds.")
            time.sleep(interval*60)
        
        return jsonify({"success": True, "message": "Crew kickoff started."})
    except Exception as e:
        kickoff_initiated = False
        logger.error(f"Error during crew kickoff: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/twitter/kickoff-status', methods=['GET'])
def kickoff_status():
    is_active = kickoff_initiated
    return jsonify({"kickoffActive": is_active})
    
    

@app.route('/next-post-time', methods=['GET'])
def get_next_post_time():
    if kickoff_initiated and start_time and waiting_time is not None:
        return jsonify({"nextPostTime": waiting_time, "nextActionTime": actions_waiting_time})
    else:
        return jsonify({"error": "Crew is not running"}), 404
    
