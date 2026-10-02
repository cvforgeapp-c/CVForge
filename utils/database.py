import os
from prisma import Prisma

# Initialize Global Prisma Client
db = Prisma()

def connect_db():
    """Connects to PostgreSQL database if not already connected."""
    if not db.is_connected():
        db.connect()

def disconnect_db():
    """Gracefully disconnects from PostgreSQL database."""
    if db.is_connected():
        db.disconnect()
