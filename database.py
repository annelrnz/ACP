# database.py
import sqlite3
import os

def init_db():
    """Initialize database with section support"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Drop and recreate tables to ensure correct structure
    cursor.execute('DROP TABLE IF EXISTS students')
    cursor.execute('DROP TABLE IF EXISTS attendance_records')
    
    # Students table with ALL required columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            section TEXT NOT NULL,
            block TEXT NOT NULL,
            gsuite TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Attendance records with section
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course_code TEXT,
            section TEXT,
            class_time TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
   
    try:

        sample_students = [
        ('24-02453', 'John Doe', 'CPE405', 'A', 'Block 1', 'john.doe@example.com'),
        ('24-02454', 'Jane Smith', 'CPE405', 'A', 'Block 1', 'jane.smith@example.com'),
        ('24-02455', 'Mike Johnson', 'IT2104', 'B', 'Block 2', 'mike.johnson@example.com')
    ]
        for student in sample_students:
            cursor.execute('''
            INSERT OR IGNORE INTO students 
            (student_id, name, course, section, block, gsuite) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', student)
        
        conn.commit()
        print("✅ Database initialized with sample data!")
    except:
        print("✅ Database initialized!")
    
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect('attendify.db')