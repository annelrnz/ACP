# student_crud.py
import sqlite3
from tkinter import messagebox
from database import create_connection
import qrcode

def add_student(student_id, name, course, section):
    """CREATE: Add a new student to the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (student_id, name, course, section)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, course, section))
            conn.commit()
            print(f"Student {name} added successfully!")
            return True
        except sqlite3.IntegrityError:
            print("Error: Student ID already exists!")
            return False
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    return False

def generate_qr_code(self):
        """Generates a QR code from student details and displays it in a pop-up window."""
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        course = self.course_entry.get().strip()
        section = self.section_entry.get().strip()

        # Combine all relevant data into a single string for the QR code
        qr_data = f"ID: {student_id}, Name: {name}, Course: {course}, Section: {section}"

        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID to generate a QR code!")
            return

        try:
            # Generate the QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Create a Toplevel window (pop-up)
            qr_window = tk.Toplevel(self.root)
            qr_window.title("Generated QR Code")
            
            # Convert PIL Image to a Tkinter PhotoImage
            self.qr_photo = ImageTk.PhotoImage(img) # Must keep a reference to prevent garbage collection

            # Display the image in a Label
            qr_label = tk.Label(qr_window, image=self.qr_photo)
            qr_label.pack(padx=20, pady=20)
            
            # Add a label with the data below the QR code
            data_label = tk.Label(qr_window, text=qr_data, wraplength=300)
            data_label.pack(padx=20, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {e}")

def get_all_students():
    """READ: Get all students from database"""
    conn = create_connection()
    students = []
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT student_id, name, course, section, date_created 
                FROM students 
                ORDER BY name
            ''')
            students = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return students

def get_student_by_id(student_id):
    """READ: Get a specific student by ID"""
    conn = create_connection()
    student = None
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT student_id, name, course, section 
                FROM students 
                WHERE student_id = ?
            ''', (student_id,))
            student = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return student

def update_student(student_id, new_name=None, new_course=None, new_section=None):
    """UPDATE: Modify an existing student's information"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Build the update query dynamically based on provided fields
            updates = []
            params = []
            
            if new_name is not None:
                updates.append("name = ?")
                params.append(new_name)
            if new_course is not None:
                updates.append("course = ?")
                params.append(new_course)
            if new_section is not None:
                updates.append("section = ?")
                params.append(new_section)
            
            if updates:  # Only update if there are changes
                params.append(student_id)  # WHERE clause parameter
                
                update_query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
                cursor.execute(update_query, params)
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"Student {student_id} updated successfully!")
                    return True
                else:
                    print("Error: Student not found!")
                    return False
            else:
                print("No changes provided!")
                return False
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    return False

#delete student function to 
def delete_student(student_id):
    """DELETE: Remove a student from the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # First, check if student exists
            cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()
            
            if student:
                # Delete the student
                cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                conn.commit()
                print(f"Student {student[0]} (ID: {student_id}) deleted successfully!")
                return True
            else:
                print("Error: Student not found!")
                return False
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    return False

