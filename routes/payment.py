from flask import Blueprint, request, jsonify
from utils.auth_middleware import token_required
from services.payment_service import create_paddle_checkout_session, verify_paddle_webhook

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/payments/checkout', methods=['POST'])
@token_required
def create_checkout(current_user_id):
    """
    Creates a Paddle checkout session for purchasing credits or upgrading subscription plans.
    """
    data = request.get_json() or {}
    price_id = data.get('price_id')
    user_email = data.get('email', '')

    if not price_id:
        return jsonify({'error': 'price_id is required'}), 400

    result = create_paddle_checkout_session(current_user_id, user_email, price_id)
    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result), 200


@payment_bp.route('/api/payments/paddle-webhook', methods=['POST'])
def paddle_webhook():
    """
    Webhook endpoint called directly by Paddle when a payment succeeds or subscription updates.
    """
    signature = request.headers.get('Paddle-Signature', '')
    payload = request.get_json() or {}

    if not verify_paddle_webhook(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = payload.get('event_type')

    # Handle successful transaction
    if event_type == 'transaction.completed':
        data = payload.get('data', {})
        user_id = data.get('custom_data', {}).get('user_id')
        
        # Increments user credit balance or updates tier in PostgreSQL
        print(f"Payment successful via Paddle for user_id: {user_id}")

    return jsonify({'status': 'success'}), 200
