import os
import yaml
import google.oauth2.credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI
from flask import jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
import ast

def get_authenticated_service():
    try:
        credentials = load_credentials_from_yaml('config.yaml')
    except ValueError as e:
        print(f"Error loading credentials: {e}")
        credentials = get_new_credentials()
        save_credentials_to_yaml(credentials, 'config.yaml')

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                save_credentials_to_yaml(credentials, 'config.yaml')
            except google.auth.exceptions.RefreshError as e:
                print(f"Error refreshing credentials: {e}")
                credentials = get_new_credentials()
                save_credentials_to_yaml(credentials, 'config.yaml')
        else:
            print("Credentials are not valid, getting new credentials")
            credentials = get_new_credentials()
            save_credentials_to_yaml(credentials, 'config.yaml')

    return build("youtube", "v3", credentials=credentials)

def load_credentials_from_yaml(config_path):
    with open(config_path, 'r') as config_file:
        credentials_data = yaml.safe_load(config_file)
        # Ensure all necessary fields are present
        if not all(key in credentials_data for key in ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']):
            print("Missing necessary credential fields in the YAML file.")
        return google.oauth2.credentials.Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )

def get_new_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_1098259257856-1bkfr683cp83gfi98l1jn6lliqnokvha.apps.googleusercontent.com.json',  # Path to your client_secret.json file
        scopes=['https://www.googleapis.com/auth/youtube.upload'],
        access_type='offline',  # Request offline access to get a refresh token
    )
    credentials = flow.run_local_server(port=0)
    return credentials

def save_credentials_to_yaml(credentials, config_path):
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    with open(config_path, 'w') as config_file:
        yaml.safe_dump(credentials_data, config_file)

def upload_video(file):
    youtube_service = get_authenticated_service()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    file_path = "svideo/video.mp4"
    category_id = "24"
    privacy_status = "public"

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid file path"}), 400
    
    with open("svideo/svideo_plot.txt", 'r') as plot_file:
        plot_content = plot_file.read()
    print(plot_content)

    title = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate a YouTube video title based on the following plot: {plot_content}. Return only title, no additional text, no quotes. No more than 5 words. Examples: 'Finally, you know it', 'Did you know that...', 'How is it possible?', 'How is it possible?', 'Why you leave your footwear outside a temple?', 'Shocking Link Found Between Ancient India and The Mayan Civilization'."}]
            )
    
    description = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate a YouTube video description based on the following plot: {plot_content}. Return only description, no additional text, no quotes. No more than 25 words."}]
            )
    
    tags_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate a YouTube video tags based on the following plot: {plot_content}. Return only tags, no additional text, no quotes. No more than 5 tags. Return array of tags. Examples: ['ancient india', 'mayan civilization', 'shocks', 'ancient history', 'ancient civilizations']."}]
            )
    
    print(tags_response.choices[0].message.content)
    tags_string = tags_response.choices[0].message.content 
    tags = ast.literal_eval(tags_string)
    request_body = {
        "snippet": {
            "title": title.choices[0].message.content + " #Shorts",
            "description": description.choices[0].message.content,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "contentRating": {
                "ytRating": "ytAgeRestricted"
            }
        }
    }

    media_file = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube_service.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )
    response = request.execute()
    print(response)
    # print("\n" + "="*30)
    # print("Making a video emulation...")
    # print("="*30 + "\n")
    svideo_dir = "svideo/"
    for svideo_file in os.listdir(svideo_dir):
        file_path = os.path.join(svideo_dir, svideo_file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    return {"status": "success", "message": "Video uploaded successfully"}