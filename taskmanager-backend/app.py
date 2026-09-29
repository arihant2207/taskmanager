import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes.tasks import tasks_bp

load_dotenv()

app = Flask(__name__)

allowed_origins = [
    "http://localhost:3000",
    "https://taskmanager-blond-nine.vercel.app"
]

CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

# Register tasks blueprint (/api)
app.register_blueprint(tasks_bp)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/ping', methods=['GET'])
def ping():
    print("PING ROUTE HIT", flush=True)
    return jsonify({"message": "pong"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
