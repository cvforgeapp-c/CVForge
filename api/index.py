import sys
import os

# Guarantee project root directory is in system path regardless of execution directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for cross-origin requests (e.g., Next.js frontend)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import route blueprints dynamically/safely
    try:
        from routes.auth import auth_bp
        from routes.cover_letter import cover_letter_bp
        from routes.optimize import optimize_bp
        from routes.payment import payment_bp
        from routes.stream import stream_bp

        # Register blueprints with /api prefix
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(cover_letter_bp, url_prefix="/api/cover-letter")
        app.register_blueprint(optimize_bp, url_prefix="/api/optimize")
        app.register_blueprint(payment_bp, url_prefix="/api/payment")
        app.register_blueprint(stream_bp, url_prefix="/api/stream")
    except ImportError as e:
        print(f"[Warning] Failed to register some routes: {e}")

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok", 
            "service": "CVForge Backend",
            "routes_loaded": list(app.blueprints.keys())
        })

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    
    print(f"\n🚀 Starting CVForge Backend on http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
