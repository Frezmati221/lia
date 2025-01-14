from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google_auth_oauthlib.flow
import os
import re
from flask import jsonify, redirect, url_for, session, request
from lia.crews.svideo_crew import SVideoCrew
import google.auth
from google_auth_oauthlib.flow import Flow
import yaml
import google.oauth2.credentials
import time
import random
from ..config import read_config
from openai import OpenAI
from oauthlib.oauth2.rfc6749.errors import InsecureTransportError

# Define YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
youtube_kickoff_initiated = False
youtube_start_time = None
youtube_waiting_time = None

def get_authenticated_service():
    credentials = load_credentials_from_yaml('config.yaml')
    return build("youtube", "v3", credentials=credentials)

def load_credentials_from_yaml(config_path):
    with open(config_path, 'r') as config_file:
        credentials_data = yaml.safe_load(config_file)
        return google.oauth2.credentials.Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )


flow = Flow.from_client_secrets_file(
    'client_secret_1098259257856-1bkfr683cp83gfi98l1jn6lliqnokvha.apps.googleusercontent.com.json',
    scopes=SCOPES,
    redirect_uri='https://314a-74-116-32-39.ngrok-free.app/api/youtube/callback'
)

def is_logged_in():
    try:
        credentials = load_credentials_from_yaml('config.yaml')
        return credentials and credentials.valid
    except Exception:
        return False

def register_youtube_kickoff_routes(app):   
    @app.route('/api/youtube/start', methods=['POST'])
    def youtube_kickoff():
        global youtube_kickoff_initiated, youtube_start_time, youtube_waiting_time
        if youtube_kickoff_initiated:
            return jsonify({"success": False, "message": "YouTube crew is already running."}), 400
        youtube_kickoff_initiated = True
        youtube_start_time = time.time()
        # Load the interval values from config.yaml
        config_data = read_config()
        min_interval = config_data.get('YOUTUBE_POST_INTERVAL_MIN', 0)
        max_interval = config_data.get('YOUTUBE_POST_INTERVAL_MAX', 0)

        youtube_waiting_time = random.randint(min_interval, max_interval) * 60
        print("\n" + "="*30)
        print(f"Waiting for {youtube_waiting_time} seconds before starting YouTube crew...")
        print("="*30 + "\n")
        time.sleep(youtube_waiting_time)

        try:
            while youtube_kickoff_initiated:  # Loop to keep the crew running
                log_dir = os.getenv('VIDEO_EXCLUDE_TOPICS_PATH') + "/"
                base_filename = 'svideo_exclude_topic'
                extension = '.txt'
                
                existing_files = os.listdir(log_dir)
                matching_files = [
                    f for f in existing_files 
                    if re.match(rf"{base_filename}_(\d+){extension}", f)
                ]
                
                combined_file_path = os.path.join(log_dir, f"{base_filename}_combined{extension}")
                
                exclude_topics_content = ""
                if os.path.exists(combined_file_path):
                    with open(combined_file_path, 'r') as combined_file:
                        exclude_topics_content = combined_file.read()
                
                if matching_files:
                    for file_name in matching_files:
                        with open(os.path.join(log_dir, file_name), 'r') as file:
                            exclude_topics_content += file.read() + "\n"
                    
                    # Write the updated content back to the combined file
                    with open(combined_file_path, 'w') as combined_file:
                        combined_file.write(exclude_topics_content)
                    
                    for file_name in matching_files:
                        os.remove(os.path.join(log_dir, file_name))
                
                SVideoCrew().crew().kickoff(inputs={
                    'domain': 'history,world,science,technology,art,literature,music,philosophy,religion,culture,sports,controvertial theories, mysteries, and conspiracies, myths, legends, and folklore.',
                    'exclude_topics': exclude_topics_content
                })

                # Wait for the next interval
                min_interval = config_data.get('YOUTUBE_POST_INTERVAL_MIN', 0)
                max_interval = config_data.get('YOUTUBE_POST_INTERVAL_MAX', 0)
                youtube_waiting_time = random.randint(min_interval, max_interval) * 60
                youtube_start_time = time.time()
                print("\n" + "="*30)
                print(f"Waiting for {youtube_waiting_time} seconds before making the next video emulation...")
                print("="*30 + "\n")
                time.sleep(youtube_waiting_time) 

            return jsonify({"success": True, "message": "YouTube crew kickoff started."})
        except Exception as e:
            youtube_kickoff_initiated = False
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/youtube/stop', methods=['POST'])
    def stop_youtube_crew():
        global youtube_kickoff_initiated
        if not youtube_kickoff_initiated:
            return jsonify({"success": False, "message": "YouTube crew is not running."}), 400
        
        print("\n" + "="*30)
        print("YouTube crew has been stopped successfully.")
        print("="*30 + "\n")

        youtube_kickoff_initiated = False
        return jsonify({"success": True, "message": "YouTube crew has been stopped successfully."}) 

    @app.route('/api/youtube/login')
    def login():
        authorization_url, state = flow.authorization_url(access_type='offline')
        session['state'] = state
        return jsonify({"success": True, "authUrl": authorization_url})

    @app.route('/api/youtube/callback')
    def oauth2callback():
        try:
            flow.fetch_token(authorization_response=request.url.replace("http://", "https://"))
            credentials = flow.credentials
            save_credentials_to_yaml(credentials)
            return redirect('http://localhost:3000')
 
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    def save_credentials_to_yaml(credentials):
        config_path = 'config.yaml'
        existing_credentials = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                existing_credentials = yaml.safe_load(config_file) or {}
        
        existing_credentials.update(credentials_to_dict(credentials))
        
        with open(config_path, 'w') as config_file:
            yaml.dump(existing_credentials, config_file)

    def credentials_to_dict(credentials):
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    @app.route('/api/youtube/login_status', methods=['GET'])
    def login_status():
        logged_in = is_logged_in()
        return jsonify({"loginRequired": not logged_in})

    @app.route('/api/youtube/next_post_time', methods=['GET'])
    def get_next_post_time_youtube():
        if not youtube_kickoff_initiated:
            return jsonify({"success": False, "message": "YouTube crew is not running."}), 400

        response = {"success": True}

        if youtube_waiting_time is not None and youtube_start_time is not None:
            response["next_post_time"] = youtube_start_time + youtube_waiting_time
        # else:
        #     response["next_post_time"] = "Next post time is not set."

        return jsonify(response)

