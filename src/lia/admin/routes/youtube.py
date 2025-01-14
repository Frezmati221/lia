import yaml
from flask import jsonify, request


def register_youtube_routes(app):
    @app.route('/api/youtube/settings', methods=['GET'])
    def serve_youtube_settings():
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        youtube_settings = {
            "min_upload_interval": config.get("YOUTUBE_POST_INTERVAL_MIN"),
            "max_upload_interval": config.get("YOUTUBE_POST_INTERVAL_MAX"),
           
        }
        return jsonify(youtube_settings)

    @app.route('/api/youtube/settings', methods=['POST'])
    def update_settings_youtube():
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        # Parse incoming JSON data
        data = request.json

        # Extract values for minInterval and maxInterval, ensure they are integers
        min_interval = int(data.get("min_upload_interval"))
        max_interval = int(data.get("max_upload_interval"))

        if min_interval > max_interval:
            return jsonify({"success": False, "message": "min_interval cannot be greater than max_interval"}), 400

        config["YOUTUBE_POST_INTERVAL_MIN"] = min_interval
        config["YOUTUBE_POST_INTERVAL_MAX"] = max_interval

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(config, file)

        return jsonify({"success": True, "message": "Settings updated successfully."})