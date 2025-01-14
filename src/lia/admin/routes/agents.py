from flask import jsonify, request

agents = [{"id": 1, "name": "Nova", "status": "waiting"}]

def register_agent_routes(app):
    @app.route('/api/agents', methods=['GET'])
    def get_agents():
        return jsonify({"agents": agents})

    @app.route('/api/youtube/agents', methods=['GET'])
    def get_youtube_agents():
        return jsonify({"agents": agents})
