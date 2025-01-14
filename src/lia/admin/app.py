from flask import Flask
import logging
from flask_cors import CORS
from dotenv import load_dotenv
import threading
from .routes.agents import register_agent_routes
from .routes.kickoff import register_kickoff_routes
from .routes.twitter import register_twitter_routes
from .routes.logs import register_log_routes
from .routes.youtube_kickoff import register_youtube_kickoff_routes
from .routes.youtube import register_youtube_routes
load_dotenv()

# Example log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Flask app started")

app = Flask(__name__)
app.secret_key = "secret"
CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes
register_agent_routes(app)
register_kickoff_routes(app)
register_twitter_routes(app)
register_log_routes(app)
register_youtube_routes(app)
register_youtube_kickoff_routes(app)

if __name__ == "__main__":
    app.run()
    
    
