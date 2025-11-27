# models.py
import sqlite3
from database import get_connection
from datetime import datetime

class Student:
    @staticmethod
    def get_all_sections():
        """Get all unique sections from database"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT section FROM students WHERE section IS NOT NULL AND section != '' ORDER BY section")
            sections = [row[0] for row in cursor.fetchall()]
            return sections
        except Exception as e:
            print(f"Error getting sections: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_students_by_section(section):
        """Get all students in a specific section"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM students WHERE section = ? ORDER BY name", (section,))
            students = cursor.fetchall()
            return students
        except Exception as e:
            print(f"Error getting students by section: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_student_count_by_section(section):
        """Get number of students in a section"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM students WHERE section = ?", (section,))
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error counting students: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def create(student_data):
        """Create new student with section"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Make sure block has a default value if empty
            block = student_data.get('block', '').strip()
            if not block:
                block = "N/A"
                
            cursor.execute('''
                INSERT INTO students (student_id, name, course, section, block, gsuite)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                student_data['student_id'],
                student_data['name'],
                student_data['course'],
                student_data['section'],
                block,
                student_data['gsuite']
            ))
            conn.commit()
            return True, "Student added successfully!"
        except sqlite3.IntegrityError:
            return False, "Student ID already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def get_all_courses():
        """Get all unique courses from database"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT course FROM students WHERE course IS NOT NULL AND course != '' ORDER BY course")
            courses = [row[0] for row in cursor.fetchall()]
            return courses
        except Exception as e:
            print(f"Error getting courses: {e}")
            return ["CPE405", "IT2104", "CS201"]  # Fallback
        finally:
            conn.close()
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()
            return student
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete_student(student_id):
        """Delete student by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            return True, "Student deleted successfully!"
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
        finally:
            conn.close()


class Attendance:
    @staticmethod
    def mark_attendance(student_id, course_code, section, class_time):
        """Mark attendance for a student"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Check if attendance already marked for today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM attendance_records 
                WHERE student_id = ? AND course_code = ? AND section = ? AND date(timestamp) = ?
            ''', (student_id, course_code, section, today))
            
            if cursor.fetchone():
                return False, "Attendance already marked for today"
            
            # Mark attendance
            cursor.execute('''
                INSERT INTO attendance_records (student_id, course_code, section, class_time)
                VALUES (?, ?, ?, ?)
            ''', (student_id, course_code, section, class_time))
            
            conn.commit()
            return True, "Attendance marked successfully!"
        except Exception as e:
            return False, f"Error marking attendance: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def get_today_attendance(section):
        """Get today's attendance for a section"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT ar.*, s.name 
                FROM attendance_records ar
                JOIN students s ON ar.student_id = s.student_id
                WHERE ar.section = ? AND date(ar.timestamp) = ?
                ORDER BY ar.timestamp
            ''', (section, today))
            
            attendance = cursor.fetchall()
            return attendance
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_attendance_count(section):
        """Get today's attendance count for a section"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM attendance_records 
                WHERE section = ? AND date(timestamp) = ?
            ''', (section, today))
            
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error counting attendance: {e}")
            return 0
        finally:
            conn.close()