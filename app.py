import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import utilities
from utils.database import db

# Import backend route blueprints
from routes.auth import auth_bp
from routes.cover_letter import cover_letter_bp
from routes.optimize import optimize_bp
from routes.payment import payment_bp
from routes.stream import stream_bp

# Load environment secrets
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Configure CORS to communicate seamlessly with Next.js frontend
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Register Blueprints with explicit API prefixes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(cover_letter_bp, url_prefix='/api/cover-letter')
app.register_blueprint(optimize_bp, url_prefix='/api/optimize')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(stream_bp, url_prefix='/api/stream')

# Health Check Endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "CVForge Backend API",
        "version": "1.0.0"
    }), 200

# Global Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
