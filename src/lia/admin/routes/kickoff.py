from flask import jsonify
import time
import random
import yaml
from lia.crews.twitter_crew import Lia
from lia.characters.lia import characterLia
from lia.crews.twitter_actions import LiaTwitterActions
import logging

logger = logging.getLogger(__name__)


kickoff_initiated = False
start_time = None
waiting_time = None
agents = [{"id": 1, "name": "Nova", "status": "waiting"}]
kickoff_initiated_actions = False
start_time_actions = None
waiting_time_actions = None

def register_kickoff_routes(app):
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

    @app.route('/api/twitter/start', methods=['POST'])
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

            while kickoff_initiated:
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
                start_time = time.time()
                waiting_time = interval*60

                print(f"Next kickoff in {interval*60} seconds.")
                time.sleep(interval*60)
            
            return jsonify({"success": True, "message": "Crew kickoff started."})
        except Exception as e:
            kickoff_initiated = False
            logger.error(f"Error during crew kickoff: {e}")
            return jsonify({"success": False, "error": str(e)}), 500 

    @app.route('/api/twitter/stop', methods=['POST'])
    def stop_twitter_crew():
        global kickoff_initiated, waiting_time, start_time
        if not kickoff_initiated:
            return jsonify({"success": False, "message": "Crew is not running."}), 400

        kickoff_initiated = False
        waiting_time = None
        start_time = None
        logger.info("Twitter crew has been stopped.")
        print("\n" + "="*30)
        print("Twitter crew has been stopped.")
        print("="*30 + "\n")
        return jsonify({"success": True, "message": "Crew has been stopped successfully."}) 

    @app.route('/api/twitter/next_post_time', methods=['GET'])
    def get_next_post_time():
        if not kickoff_initiated and not kickoff_initiated_actions:
            return jsonify({"success": False, "message": "Crew is not running."}), 400

        response = {"success": True}

        if waiting_time is not None and start_time is not None:
            response["next_post_time"] = start_time + waiting_time
        # else:
            # response["next_post_time"] = "Next post time is not set."

        if waiting_time_actions is not None and start_time_actions is not None:
            response["next_actions_time"] = start_time_actions + waiting_time_actions
        # else:
        #     response["next_actions_time"] = "Next actions time is not set."

        return jsonify(response)

    @app.route('/api/twitter_actions/start', methods=['POST'])
    def start_twitter_actions_crew():
        global kickoff_initiated_actions, start_time_actions, waiting_time_actions
        if kickoff_initiated_actions:
            return jsonify({"success": False, "message": "Twitter actions crew is already running."}), 400

        kickoff_initiated_actions = True
        start_time_actions = time.time()

        print("\n" + "="*30)
        print("Starting twitter actions crew...")
        print("="*30 + "\n")

        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            min_interval = config.get("TWITTER_ACTION_INTERVAL_MIN", 1)
            max_interval = config.get("TWITTER_ACTION_INTERVAL_MAX", 2)
            interval = random.randint(min_interval, max_interval)
            print("\n" + "="*30)
            print(f"Initial wait for {interval*60} seconds before first kickoff.")
            print("="*30 + "\n")
            waiting_time_actions = interval*60
            time.sleep(interval*60)

            while kickoff_initiated_actions:
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
                # LiaTwitterActions().crew().kickoff(inputs=inputs)
                print("\n" + "="*30)
                print("Kickoff initiated")
                print("="*30 + "\n")

                min_interval = int(config.get("TWITTER_ACTION_INTERVAL_MIN", 1))
                max_interval = int(config.get("TWITTER_ACTION_INTERVAL_MAX", 2))
                interval = random.randint(min_interval, max_interval)
                start_time_actions = time.time()
                waiting_time_actions = interval*60

                print(f"Next kickoff in {interval*60} seconds.")
                time.sleep(interval*60)

            return jsonify({"success": True, "message": "Twitter actions crew kickoff started."})
        except Exception as e:
            kickoff_initiated_actions = False
            logger.error(f"Error during twitter actions crew kickoff: {e}")
            return jsonify({"success": False, "error": str(e)}), 500 

    @app.route('/api/twitter_actions/stop', methods=['POST'])
    def stop_twitter_actions_crew():
        global kickoff_initiated_actions, waiting_time_actions, start_time_actions
        if not kickoff_initiated_actions:
            return jsonify({"success": False, "message": "Twitter actions crew is not running."}), 400

        kickoff_initiated_actions = False
        waiting_time_actions = None
        start_time_actions = None
        logger.info("Twitter actions crew has been stopped.")
        print("\n" + "="*30)
        print("Twitter actions crew has been stopped.")
        print("="*30 + "\n")
        return jsonify({"success": True, "message": "Twitter actions crew has been stopped successfully."}) 