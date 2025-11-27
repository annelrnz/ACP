# reset_db.py
import sqlite3
import os

def reset_database():
    """Completely reset the database with correct schema"""
    if os.path.exists('attendify.db'):
        os.remove('attendify.db')
        print("Old database deleted")
    
    # Reinitialize with correct schema
    from database import init_db
    init_db()
    print("New database created with correct schema!")

if __name__ == "__main__":
    reset_database()