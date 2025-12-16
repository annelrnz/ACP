# models.py
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
            
            # Record attendance in attendance_records table
            cursor.execute('''
                INSERT INTO attendance_records 
                (student_id, course_code, section, class_time, timestamp) 
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (student_id, course_code, section, class_time))
            
            # Get student name for history
            cursor.execute('SELECT name FROM students WHERE student_id = ?', (student_id,))
            student = cursor.fetchone()
            name = student[0] if student else student_id
            
            # Also record in attendance_history table
            current_datetime = datetime.now()
            attendance_date = current_datetime.strftime('%Y-%m-%d')
            attendance_time = current_datetime.strftime('%H:%M:%S')
            
            cursor.execute('''
                INSERT INTO attendance_history 
                (student_id, name, course_code, section, attendance_date, attendance_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, course_code, section, attendance_date, attendance_time, 'Present'))
            
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

class AttendanceHistory:
    @staticmethod
    def record_attendance(student_id, name, course_code, section):
        """Record detailed attendance with date and time"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            current_datetime = datetime.now()
            attendance_date = current_datetime.strftime('%Y-%m-%d')
            attendance_time = current_datetime.strftime('%H:%M:%S')
            
            cursor.execute('''
                INSERT INTO attendance_history 
                (student_id, name, course_code, section, attendance_date, attendance_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, course_code, section, attendance_date, attendance_time, 'Present'))
            
            conn.commit()
            conn.close()
            return True, "Attendance recorded in history!"
        except Exception as e:
            return False, f"Error recording attendance history: {str(e)}"
    
    @staticmethod
    def get_student_attendance_history(student_id, course_code=None):
        """Get detailed attendance history for a student"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if course_code:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE student_id = ? AND course_code = ?
                    ORDER BY attendance_date DESC, attendance_time DESC
                '''
                params = (student_id, course_code)
            else:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE student_id = ?
                    ORDER BY attendance_date DESC, attendance_time DESC
                '''
                params = (student_id,)
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            
            # Format the records
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'id': record[0],
                    'student_id': record[1],
                    'name': record[2],
                    'course_code': record[3],
                    'section': record[4],
                    'date': record[5],
                    'time': record[6],
                    'status': record[7],
                    'notes': record[8]
                })
            
            return formatted_records
        except:
            return []
    
    @staticmethod
    def get_section_attendance_history(section, date=None, course_code=None):
        """Get attendance history for a section"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if date and course_code:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE section = ? AND attendance_date = ? AND course_code = ?
                    ORDER BY attendance_time ASC
                '''
                params = (section, date, course_code)
            elif date:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE section = ? AND attendance_date = ?
                    ORDER BY attendance_time ASC
                '''
                params = (section, date)
            elif course_code:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE section = ? AND course_code = ?
                    ORDER BY attendance_date DESC, attendance_time ASC
                '''
                params = (section, course_code)
            else:
                query = '''
                    SELECT * FROM attendance_history 
                    WHERE section = ?
                    ORDER BY attendance_date DESC, attendance_time ASC
                '''
                params = (section,)
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            
            return records
        except Exception as e:
            print(f"Error getting section attendance history: {e}")
            return []
    
    @staticmethod
    def get_daily_attendance_report(date=None):
        """Get daily attendance report"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if date:
                query = '''
                    SELECT 
                        section,
                        course_code,
                        COUNT(DISTINCT student_id) as total_students,
                        COUNT(*) as total_attendances
                    FROM attendance_history 
                    WHERE attendance_date = ?
                    GROUP BY section, course_code
                    ORDER BY section, course_code
                '''
                params = (date,)
            else:
                query = '''
                    SELECT 
                        attendance_date,
                        section,
                        course_code,
                        COUNT(DISTINCT student_id) as total_students,
                        COUNT(*) as total_attendances
                    FROM attendance_history 
                    GROUP BY attendance_date, section, course_code
                    ORDER BY attendance_date DESC, section, course_code
                '''
                params = ()
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            
            return records
        except:
            return []