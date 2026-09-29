from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    credits_balance = db.Column(db.Integer, default=3)  # 3 free credits on signup
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    resumes = db.relationship('Resume', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), default="Untitled Resume")
    original_text = db.Column(db.Text, nullable=True)
    tailored_text = db.Column(db.Text, nullable=True)
    match_score = db.Column(db.Integer, default=0)
    job_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paddle_transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    credits_added = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
