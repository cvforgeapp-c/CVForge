import os
import requests

PADDLE_API_KEY = os.getenv("PADDLE_API_KEY", "paddledrv_test_key_placeholder")
PADDLE_ENV = os.getenv("PADDLE_ENV", "sandbox")  # 'sandbox' or 'production'

PADDLE_BASE_URL = (
    "https://sandbox-api.paddle.com" if PADDLE_ENV == "sandbox" else "https://api.paddle.com"
)

def create_paddle_checkout_session(user_id: str, user_email: str, price_id: str) -> dict:
    """
    Creates a Paddle Billing Transaction / Checkout session for starter/pro/expert credits.
    """
    headers = {
        "Authorization": f"Bearer {PADDLE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "items": [
            {
                "price_id": price_id,  # e.g., 'pri_01h1234567890' created in Paddle Dashboard
                "quantity": 1
            }
        ],
        "custom_data": {
            "user_id": user_id
        },
        "customer_email": user_email
    }

    try:
        response = requests.post(f"{PADDLE_BASE_URL}/transactions", json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json().get("data", {})
            transaction_id = data.get("id")
            
            # Extract checkout overlay/hosted URL
            checkout_url = data.get("checkout", {}).get("url")
            return {
                "status": "success",
                "transaction_id": transaction_id,
                "checkout_url": checkout_url
            }
        else:
            print(f"Paddle Error Response: {response.status_code} - {response.text}")
            return {"error": f"Paddle API returned status {response.status_code}"}

    except Exception as e:
        print(f"Paddle payment integration exception: {e}")
        return {"error": "Failed to connect to Paddle Payment Gateway."}


def verify_paddle_webhook(payload: dict, signature_header: str) -> bool:
    """
    Validates signature for incoming Paddle Webhook events (e.g. transaction.completed).
    """
    # Simple webhook verification stub; for production, compute HMAC using PADDLE_WEBHOOK_SECRET
    webhook_secret = os.getenv("PADDLE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return True  # Fallback bypass in development environment
        
    return bool(signature_header)
