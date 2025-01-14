from flask import jsonify, request, redirect, session
import os
import yaml
from requests_oauthlib import OAuth1Session
from lia.clients.client_twitter_off import login as loginTwitter, save_tokens
from lia.admin.config import read_config
import logging

logger = logging.getLogger(__name__)

def register_twitter_routes(app):
    @app.route('/api/twitter/login', methods=['GET'])
    def twitter_login():
        try:
            authUrl, oauth_token, oauth_token_secret = loginTwitter()
            
            session['oauth_token'] = oauth_token
            session['oauth_token_secret'] = oauth_token_secret
            
            return jsonify({"success": True, "authUrl": authUrl})
        except Exception as e:
            logger.error(f"Error during Twitter login: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/twitter/settings', methods=['GET'])
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

    @app.route('/api/twitter/settings', methods=['POST'])
    def update_settings():
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        # Parse incoming JSON data
        data = request.json

        # Extract values for minInterval and maxInterval, ensure they are integers
        min_interval = int(data.get("min_interval"))
        max_interval = int(data.get("max_interval"))
        action_min_interval = int(data.get("action_min_interval"))
        action_max_interval = int(data.get("action_max_interval"))

        if min_interval > max_interval:
            return jsonify({"success": False, "message": "min_interval cannot be greater than max_interval"}), 400
        if action_min_interval > action_max_interval:
            return jsonify({"success": False, "message": "action_min_interval cannot be greater than action_max_interval"}), 400

        config["TWITTER_POST_INTERVAL_MIN"] = min_interval
        config["TWITTER_POST_INTERVAL_MAX"] = max_interval
        config["TWITTER_ACTION_INTERVAL_MIN"] = action_min_interval
        config["TWITTER_ACTION_INTERVAL_MAX"] = action_max_interval

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(config, file)

        return jsonify({"success": True, "message": "Settings updated successfully."})

    @app.route('/api/twitter/callback')
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
            return redirect('http://localhost:3000')
        except Exception as e:
            logger.error(f"Error during Twitter callback: {e}")
            return jsonify({"success": False, "error": str(e)}), 500 

    @app.route('/api/twitter/status', methods=['GET'])
    def twitter_status():
        config = read_config()

        if config.get("TWITTER_ACCESS_TOKEN") and config.get("TWITTER_ACCESS_TOKEN_SECRET"):
            return jsonify({"loginRequired": False})
        else:
            return jsonify({"loginRequired": True}) 

    @app.route('/api/twitter/logs', methods=['GET'])
    def get_twitter_logs():
        try:
            log_dir = 'src/lia/admin/logs/twitter'
            files = os.listdir(log_dir)
            files = [os.path.join(log_dir, f) for f in files]
            # Sort files in reverse order by creation time
            files.sort(key=os.path.getctime, reverse=True)

            log_contents = ""
            for file in files:
                with open(file, 'r') as f:
                    log_contents += f.read() + "\n---\n"

            return log_contents
        except Exception as e:
            logger.error(f"Error retrieving Twitter logs: {e}")
            return jsonify({"success": False, "error": str(e)}), 500 