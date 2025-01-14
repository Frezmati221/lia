from flask import jsonify, render_template
import os

logs = []

def register_log_routes(app):
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

    @app.route('/')
    def serve_index():
        return render_template('index.html', logs=logs) 