import os
import datetime
import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils.auth_middleware import token_required, SECRET_KEY
import psycopg2
from psycopg2.extras import RealDictCursor

auth_bp = Blueprint('auth', __name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cvforge_db")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Email already exists.'}), 409

        cur.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash, credits_coins, credits_target)
            VALUES (%s, %s, %s, %s, 0, 1)
            RETURNING id, first_name, last_name, email, credits_coins, credits_target;
        """, (first_name, last_name, email, hashed_pw))
        
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            'message': 'Signup successful!',
            'token': token,
            'user': user
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password.'}), 401

        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': user['id'],
                'first_name': user['first_name'],
                'email': user['email'],
                'credits': {'coins': user['credits_coins'], 'target': user['credits_target']}
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/user/credits', methods=['GET'])
@token_required
def get_credits(current_user_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT credits_coins, credits_target FROM users WHERE id = %s", (current_user_id,))
        credits = cur.fetchone()
        cur.close()
        conn.close()

        if not credits:
            return jsonify({'error': 'User not found.'}), 404

        return jsonify({
            'coins': credits['credits_coins'],
            'target': credits['credits_target']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
