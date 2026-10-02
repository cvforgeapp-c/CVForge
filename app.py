import os
from flask import Flask
from flask_cors import CORS

# Import route blueprints
from routes.auth import auth_bp
from routes.stream import stream_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(stream_bp)

@app.route('/')
def health_check():
    return {"status": "CVForge Backend Running", "port": 5000}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
