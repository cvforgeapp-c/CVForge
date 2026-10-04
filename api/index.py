import sys
import os

# Add root directory to path for modules inside routes/, services/, utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify
from flask_cors import CORS

# Import route blueprints
from routes.auth import auth_bp
from routes.cover_letter import cover_letter_bp
from routes.optimize import optimize_bp
from routes.payment import payment_bp
from routes.stream import stream_bp

app = Flask(__name__)
CORS(app)

# Register blueprints with /api prefix
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(cover_letter_bp, url_prefix="/api/cover-letter")
app.register_blueprint(optimize_bp, url_prefix="/api/optimize")
app.register_blueprint(payment_bp, url_prefix="/api/payment")
app.register_blueprint(stream_bp, url_prefix="/api/stream")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "CVForge Backend"})

if __name__ == "__main__":
    app.run()
