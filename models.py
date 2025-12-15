
import sqlite3
from datetime import datetime
from database import get_connection

class Student:
    @staticmethod
    def create(student_data):
        """Create a new student record"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO students 
                (student_id, name, course, section, block, gsuite) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                student_data['student_id'],
                student_data['name'],
                student_data['course'],
                student_data['section'],
                student_data.get('block', ''),
                student_data.get('gsuite', '')
            ))
            
            conn.commit()
            conn.close()
            return True, "Student added successfully!"
        except Exception as e:
            return False, f"Error adding student: {str(e)}"
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by student_id"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM students WHERE student_id = ?
            ''', (student_id,))
            
            student = cursor.fetchone()
            conn.close()
            return student
        except:
            return None
    
    @staticmethod
    def get_students_by_section(section):
        """Get all students in a section"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM students WHERE section = ? ORDER BY student_id
            ''', (section,))
            
            students = cursor.fetchall()
            conn.close()
            return students
        except:
            return []
    
    @staticmethod
    def get_all_sections():
        """Get all unique sections"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT section FROM students 
                WHERE section IS NOT NULL AND section != '' 
                ORDER BY section
            ''')
            
            sections = [row[0] for row in cursor.fetchall()]
            conn.close()
            return sections
        except:
            return []
    
    @staticmethod
    def get_student_count_by_section(section):
        """Get number of students in a section"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM students WHERE section = ?
            ''', (section,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

class Attendance:
    @staticmethod
    def mark_attendance(student_id, course_code, section, class_time):
        """Mark attendance for a student"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Check if attendance already recorded for today
            today = datetime.now().date()
            cursor.execute('''
                SELECT * FROM attendance_records 
                WHERE student_id = ? AND course_code = ? AND DATE(timestamp) = ?
            ''', (student_id, course_code, today))
            
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                return False, "Attendance already recorded for today"
            
            # Record attendance
            cursor.execute('''
                INSERT INTO attendance_records 
                (student_id, course_code, section, class_time, timestamp) 
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (student_id, course_code, section, class_time))
            
            conn.commit()
            conn.close()
            return True, "Attendance recorded successfully!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_todays_attendance_by_section(section, course_code=None):
        """Get today's attendance count for a section"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            if course_code:
                query = '''
                    SELECT COUNT(DISTINCT student_id) 
                    FROM attendance_records 
                    WHERE section = ? AND course_code = ? AND DATE(timestamp) = ?
                '''
                params = (section, course_code, today)
            else:
                query = '''
                    SELECT COUNT(DISTINCT student_id) 
                    FROM attendance_records 
                    WHERE section = ? AND DATE(timestamp) = ?
                '''
                params = (section, today)
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    @staticmethod
    def get_attendance_records_by_section(section, date=None):
        """Get all attendance records for a section"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if date:
                query = '''
                    SELECT ar.*, s.name 
                    FROM attendance_records ar
                    JOIN students s ON ar.student_id = s.student_id
                    WHERE ar.section = ? AND DATE(ar.timestamp) = ?
                    ORDER BY ar.timestamp DESC
                '''
                params = (section, date)
            else:
                query = '''
                    SELECT ar.*, s.name 
                    FROM attendance_records ar
                    JOIN students s ON ar.student_id = s.student_id
                    WHERE ar.section = ?
                    ORDER BY ar.timestamp DESC
                '''
                params = (section,)
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            return records
        except Exception as e:
            print(f"Error getting attendance records: {e}")
            return []