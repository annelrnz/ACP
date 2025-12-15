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
            ('24-02453', 'Franz Jacob Boñon', 'BSIT', 'B', '2104', '24-02453@g.batstate-u.edu.ph'),
            ('24-02686', 'Marianne Lorenzo', 'BSIT', 'A', '2104', '24-02686@g.batstate-u.edu.ph'),
        ]
        for student in sample_students:
            cursor.execute('''
                INSERT OR IGNORE INTO students 
                (student_id, name, course, section, block, gsuite) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', student)
        
        conn.commit()
        print("✅ Database initialized with sample data")
    except:
        print("✅ Database initialized!")
    
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect('attendify.db')

def check_student(student_id):
    """Check if student exists in database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_id, name, course, section, block, gsuite 
        FROM students 
        WHERE student_id = ?
    ''', (student_id,))
    
    student = cursor.fetchone()
    conn.close()
    
    if student:
        return {
            'registered': True,
            'student_id': student[0],
            'name': student[1],
            'course': student[2],
            'section': student[3],
            'block': student[4],
            'gsuite': student[5]
        }
    else:
        return {
            'registered': False,
            'message': 'SR Code not found. Are you registered in this section? Something went wrong? Contact your professor.'
        }

def record_attendance(student_id, course_code, class_time):
    """Record attendance for a student"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if student exists
    cursor.execute('SELECT section FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return {'success': False, 'message': 'SR Code not found. Please contact your professor.'}
    
    section = student[0]
    
    try:
        cursor.execute('''
            INSERT INTO attendance_records 
            (student_id, course_code, section, class_time) 
            VALUES (?, ?, ?, ?)
        ''', (student_id, course_code, section, class_time))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Attendance recorded successfully!'}
    except Exception as e:
        conn.close()
        return {'success': False, 'message': f'Error recording attendance: {str(e)}'}