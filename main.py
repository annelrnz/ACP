import threading
import tkinter as tk
from tkinter import ttk, messagebox
from models import Student, Attendance
import qrcode
import os
import sqlite3
from PIL import Image, ImageTk
import webbrowser
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import app 

class ProfessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendify: Mark Your Presence")
        self.root.geometry("1200x750") 
        
        #pink background
        bg_color = "pink"
        self.root.configure(bg=bg_color)
        self.root.resizable(False, False)

        self.current_section = tk.StringVar()
        self.last_generated_qr = None
        self.selected_student_id = None  # Track selected student for update
        
        # Email configuration
        self.email_sender = "your-email@gmail.com"  # Change this to your Gmail
        self.email_password = "your-app-password"   # Use App Password, not regular password
        
        # Initialize QR code labels
        self.qr_label = None
        self.qr_info_label = None
        
        self.create_widgets()
        self.load_sections()
        self.setup_treeview_bindings()
    
    def create_widgets(self):
        # Configure main grid - 3 rows, 2 columns
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Student details and buttons
        self.root.grid_rowconfigure(1, weight=0)  # Statistics
        self.root.grid_rowconfigure(2, weight=1)  # Student records list
            
        # ========== ROW 0: STUDENT DETAILS AND BUTTONS ==========
        top_frame = tk.Frame(self.root, bg="pink", padx=10, pady=10)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        # Configure top frame grid
        top_frame.columnconfigure(0, weight=2)  # Entry fields get more space
        top_frame.columnconfigure(1, weight=1)  # Buttons get less space
        top_frame.rowconfigure(0, weight=1)
        
        # Entry Frame (Left side)
        entry_frame = tk.LabelFrame(top_frame, text="Student Details", font=("Arial", 10, "bold"), 
                                bg="pink", padx=15, pady=15)
        entry_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Student entry fields - organized in a grid
        tk.Label(entry_frame, text="Student ID:", bg="pink", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_id = tk.Entry(entry_frame, width=25, font=("Arial", 9))
        self.entry_id.grid(row=0, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        tk.Label(entry_frame, text="Name:", bg="pink", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(entry_frame, width=25, font=("Arial", 9))
        self.entry_name.grid(row=1, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        tk.Label(entry_frame, text="Program:", bg="pink", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_program = tk.Entry(entry_frame, width=25, font=("Arial", 9))
        self.entry_program.grid(row=2, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        tk.Label(entry_frame, text="Block:", bg="pink", font=("Arial", 9)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_block = tk.Entry(entry_frame, width=25, font=("Arial", 9))
        self.entry_block.grid(row=3, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        tk.Label(entry_frame, text="Gsuite Account:", bg="pink", font=("Arial", 9)).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_gsuite = tk.Entry(entry_frame, width=25, font=("Arial", 9))
        self.entry_gsuite.grid(row=4, column=1, pady=5, padx=(5, 0), sticky="ew")
        
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Button Frame (Right side)
        button_frame = tk.LabelFrame(top_frame, text="Actions & Section", font=("Arial", 10, "bold"), 
                                    bg="pink", padx=15, pady=15)
        button_frame.grid(row=0, column=1, sticky="nsew")
        
        # Section Management at the top of button frame
        tk.Label(button_frame, text="Section:", bg="pink", font=("Arial", 9)).pack(anchor="w", pady=(0, 5))
        
        self.section_combo = ttk.Combobox(button_frame, textvariable=self.current_section, width=22, font=("Arial", 9))
        self.section_combo.pack(fill=tk.X, pady=(0, 10))
        self.section_combo.bind('<<ComboboxSelected>>', self.on_section_change)
        self.section_combo.bind('<KeyRelease>', self.on_section_type)
        
        # Action Buttons Grid - 2 columns
        button_grid = tk.Frame(button_frame, bg="pink")
        button_grid.pack(fill=tk.BOTH, expand=True)
        
        # Column 1 buttons
        tk.Button(button_grid, text="ADD", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.add_student).grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="UPDATE", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.update_student).grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="VIEW", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.view_records).grid(row=2, column=0, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="DELETE", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.delete_student).grid(row=3, column=0, padx=2, pady=2, sticky="nsew")
        
        # Column 2 buttons
        tk.Button(button_grid, text="Refresh\nSections", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.load_sections).grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="Generate\nQR Code", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.generate_qr_code).grid(row=1, column=1, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="See QR\nCode", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.see_generated_qr).grid(row=2, column=1, padx=2, pady=2, sticky="nsew")
        tk.Button(button_grid, text="Refresh\nAttendance", font=("Arial", 9, "bold"), fg="black", bg="silver", 
                height=2, command=self.refresh_attendance_status).grid(row=3, column=1, padx=2, pady=2, sticky="nsew")
        
        # Configure button grid weights
        for i in range(4):
            button_grid.rowconfigure(i, weight=1)
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        
        # Special buttons below the grid
        special_frame = tk.Frame(button_frame, bg="pink")
        special_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(special_frame, text="⚠️ Check Inactive Students", font=("Arial", 9, "bold"), 
                fg="white", bg="#ff6b6b", height=2,
                command=self.check_inactive_students).pack(fill=tk.X, pady=2)
        
        tk.Button(special_frame, text="📧 Email Settings", font=("Arial", 9), 
                fg="black", bg="lightgray", height=1,
                command=self.configure_email_settings).pack(fill=tk.X, pady=2)
        
        # ========== ROW 1: STATISTICS ==========
        stats_frame = tk.LabelFrame(self.root, text="Section Statistics", font=("Arial", 10, "bold"), 
                                bg="pink", padx=15, pady=10)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        
        self.stats_label = tk.Label(stats_frame, text="Please select or type a section", 
                                font=("Arial", 10), bg="pink", justify=tk.LEFT, anchor="w")
        self.stats_label.pack(fill=tk.BOTH, expand=True)
        
        # ========== ROW 2: STUDENT RECORDS ==========
        bottom_frame = tk.LabelFrame(self.root, text="Student Records", font=("Arial", 10, "bold"), 
                                    bg="pink", padx=10, pady=10)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        
        # Create a frame for treeview and scrollbar
        tree_frame = tk.Frame(bottom_frame, bg="pink")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for student records
        columns = ('attendance_status', 'student_id', 'name', 'program', 'block', 'gsuite_account')
        self.tree_view = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        self.tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure column headings and widths
        self.tree_view.heading('attendance_status', text='Status')
        self.tree_view.heading('student_id', text='Student ID')
        self.tree_view.heading('name', text='Name')
        self.tree_view.heading('program', text='Program')
        self.tree_view.heading('block', text='Block')
        self.tree_view.heading('gsuite_account', text='Gsuite Account')
        
        # Column widths
        self.tree_view.column('attendance_status', anchor=tk.CENTER, width=70)
        self.tree_view.column('student_id', anchor=tk.CENTER, width=90)
        self.tree_view.column('name', anchor=tk.W, width=140)
        self.tree_view.column('program', anchor=tk.W, width=90)
        self.tree_view.column('block', anchor=tk.CENTER, width=70)
        self.tree_view.column('gsuite_account', anchor=tk.W, width=180)
        
        # Add a scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        self.tree_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize
        self.load_sections()
        self.start_flask_server()
        self.setup_treeview_bindings()

    def setup_treeview_bindings(self):
        """Setup bindings for treeview selection"""
        self.tree_view.bind('<<TreeviewSelect>>', self.on_treeview_select)

    def on_treeview_select(self, event):
        """When a student is selected in the treeview, load their data into the entry fields"""
        selected_items = self.tree_view.selection()
        if not selected_items:
            return
        
        # Get the first selected item
        item = selected_items[0]
        values = self.tree_view.item(item, 'values')
        
        if values and len(values) >= 6:
            # Store the selected student ID
            self.selected_student_id = values[1]  # student_id is at index 1
            
            # Load data into entry fields
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, values[1])  # student_id
            
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, values[2])  # name
            
            self.entry_program.delete(0, tk.END)
            self.entry_program.insert(0, values[3])  # program
            
            self.entry_block.delete(0, tk.END)
            self.entry_block.insert(0, values[4])  # block
            
            self.entry_gsuite.delete(0, tk.END)
            self.entry_gsuite.insert(0, values[5])  # gsuite_account
            
            # Highlight that we're in update mode
            self.entry_id.config(state='normal')
            self.entry_name.focus_set()

    def apply_attendance_colors(self):
        """Apply colors to attendance status in treeview"""
        for item in self.tree_view.get_children():
            values = self.tree_view.item(item)['values']
            if values and len(values) > 0:
                status = values[0]
                if "✅ Present" in status:
                    self.tree_view.item(item, tags=('present',))
                elif "❌ Absent" in status:
                    self.tree_view.item(item, tags=('absent',))
    
        # Configure tags
        self.tree_view.tag_configure('present', background='#d4edda')  # Light green
        self.tree_view.tag_configure('absent', background='#f8d7da')   # Light red

    def add_student(self):
        """Adds a new student record"""
        student_id = self.entry_id.get()
        name = self.entry_name.get()
        program = self.entry_program.get()
        block = self.entry_block.get()
        gsuite_account = self.entry_gsuite.get()

        # Create a list of fields and their names for easy iteration and user feedback
        fields_to_check = [
            (student_id, "Student ID"),
            (name, "Name"),
            (program, "Program"),
            (block, "Block"),
            (gsuite_account, "Gsuite Account")
        ]
        
        # Dapat walang field na blank
        for value, field_name in fields_to_check:
            if not value:
               # Lalabas ito kapag may hindi nilagyan na field
                messagebox.showerror("Error!", f"'{field_name}' cannot be empty.")
                return

        # Save student data
        student_data = {
            'student_id': student_id,
            'name': name,
            'course': program,
            'section': self.current_section.get() if self.current_section.get() else "Default",
            'block': block,
            'gsuite': gsuite_account
        }
        
        success, message = Student.create(student_data)
        if success:
            messagebox.showinfo("Success", "Student record added successfully!")
            self.clear_entries()
            self.refresh_student_list()  # FIXED: Added this line to refresh display
            self.load_sections()
            self.selected_student_id = None  # Clear selected student
        else:
            messagebox.showerror("Error", message)

    def view_records(self):
        """Displays all current student records in the Treeview format."""
        self.refresh_student_list()

    def update_student(self):
        """Updates an existing student record based on the Student ID."""
        # Method 1: Update using selected student from treeview
        if self.selected_student_id:
            return self.update_selected_student()
        
        # Method 2: Update using Student ID from entry field
        student_id = self.entry_id.get()
        if not student_id:
            messagebox.showerror("Error!", "Student ID cannot be empty for update.")
            return
        
        # Check if student exists
        student = Student.get_student_by_id(student_id)
        if not student:
            messagebox.showerror("Error", f"Student with ID '{student_id}' not found!")
            return
        
        # Get updated data from entry fields
        name = self.entry_name.get()
        program = self.entry_program.get()
        block = self.entry_block.get()
        gsuite_account = self.entry_gsuite.get()
        section = self.current_section.get() if self.current_section.get() else "Default"
        
        # Validate fields
        if not all([name, program, block, gsuite_account]):
            messagebox.showerror("Error!", "All fields must be filled for update.")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Update", 
                                     f"Update student {student_id}?\n\n"
                                     f"New details:\n"
                                     f"Name: {name}\n"
                                     f"Program: {program}\n"
                                     f"Section: {section}\n"
                                     f"Block: {block}\n"
                                     f"Gsuite: {gsuite_account}")
        
        if not confirm:
            return
        
        # Update student in database
        try:
            conn = sqlite3.connect('attendify.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students 
                SET name = ?, course = ?, section = ?, block = ?, gsuite = ?
                WHERE student_id = ?
            ''', (name, program, section, block, gsuite_account, student_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Student {student_id} updated successfully!")
            self.clear_entries()
            self.refresh_student_list()
            self.selected_student_id = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {str(e)}")

    def update_selected_student(self):
        """Update the currently selected student"""
        if not self.selected_student_id:
            messagebox.showerror("Error", "No student selected!")
            return
        
        # Get updated data from entry fields
        name = self.entry_name.get()
        program = self.entry_program.get()
        block = self.entry_block.get()
        gsuite_account = self.entry_gsuite.get()
        section = self.current_section.get() if self.current_section.get() else "Default"
        
        # Validate fields
        if not all([name, program, block, gsuite_account]):
            messagebox.showerror("Error!", "All fields must be filled for update.")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Update", 
                                     f"Update student {self.selected_student_id}?\n\n"
                                     f"New details:\n"
                                     f"Name: {name}\n"
                                     f"Program: {program}\n"
                                     f"Section: {section}\n"
                                     f"Block: {block}\n"
                                     f"Gsuite: {gsuite_account}")
        
        if not confirm:
            return
        
        # Update student in database
        try:
            conn = sqlite3.connect('attendify.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students 
                SET name = ?, course = ?, section = ?, block = ?, gsuite = ?
                WHERE student_id = ?
            ''', (name, program, section, block, gsuite_account, self.selected_student_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Student {self.selected_student_id} updated successfully!")
            self.clear_entries()
            self.refresh_student_list()
            self.selected_student_id = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {str(e)}")

    def delete_student(self):
        """Deletes a student record based on the Student ID."""
        student_id = self.entry_id.get()
        if not student_id:
            messagebox.showerror("Error", "Student ID cannot be empty for deletion.")
            return
        
        # Check if student exists
        student = Student.get_student_by_id(student_id)
        if not student:
            messagebox.showerror("Error", f"Student with ID '{student_id}' not found!")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete student:\n\n"
                                     f"Student ID: {student_id}\n"
                                     f"Name: {student[2] if len(student) > 2 else 'N/A'}\n\n"
                                     f"This action cannot be undone!")
        
        if not confirm:
            return
        
        # Delete student from database
        try:
            conn = sqlite3.connect('attendify.db')
            cursor = conn.cursor()
            
            # First delete attendance records for this student
            cursor.execute('DELETE FROM attendance_records WHERE student_id = ?', (student_id,))
            
            # Then delete the student
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Student {student_id} deleted successfully!")
            self.clear_entries()
            self.refresh_student_list()
            self.selected_student_id = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {str(e)}")

    def clear_entries(self):
        """Helper function to clear all input fields."""
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_program.delete(0, tk.END)
        self.entry_block.delete(0, tk.END)
        self.entry_gsuite.delete(0, tk.END)
        self.selected_student_id = None
        self.entry_id.config(state='normal')
        self.entry_id.focus_set()

    def check_inactive_students(self):
        """Check for students who have been inactive for 3 days or more"""
        section = self.current_section.get().strip()
        if not section:
            messagebox.showwarning("Warning", "Please select a section first!")
            return
        
        # Get all students in the section
        students = Student.get_students_by_section(section)
        if not students:
            messagebox.showinfo("Info", f"No students found in section {section}")
            return
        
        inactive_students = []
        today = datetime.now().date()
        
        for student in students:
            student_id = student[1]
            name = student[2]
            email = student[6]  # gsuite account
            
            # Get last attendance date
            last_attendance = self.get_last_attendance_date(student_id)
            
            if last_attendance:
                days_inactive = (today - last_attendance).days
                if days_inactive >= 3:
                    inactive_students.append({
                        'student_id': student_id,
                        'name': name,
                        'email': email,
                        'last_attendance': last_attendance,
                        'days_inactive': days_inactive
                    })
            else:
                # Student has never attended
                inactive_students.append({
                    'student_id': student_id,
                    'name': name,
                    'email': email,
                    'last_attendance': None,
                    'days_inactive': 'Never attended'
                })
        
        if not inactive_students:
            messagebox.showinfo("No Inactive Students", 
                              f"All students in section {section} have attended within the last 3 days! ✅")
            return
        
        # Show inactive students and ask if to send warnings
        self.show_inactive_students_dialog(inactive_students, section)
    
    def get_last_attendance_date(self, student_id):
        """Get the last attendance date for a student"""
        try:
            conn = sqlite3.connect('attendify.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT MAX(DATE(timestamp)) 
                FROM attendance_records 
                WHERE student_id = ?
            ''', (student_id,))
            
            result = cursor.fetchone()[0]
            conn.close()
            
            if result:
                return datetime.strptime(result, '%Y-%m-%d').date()
            return None
        except:
            return None
    
    def show_inactive_students_dialog(self, inactive_students, section):
        """Show dialog with inactive students and option to send warnings"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Inactive Students - Section {section}")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(dialog, text=f"⚠️ INACTIVE STUDENTS - SECTION {section}", 
                              font=("Arial", 14, "bold"), fg="#d63031")
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(dialog, text="Students inactive for 3+ days:", 
                           font=("Arial", 10))
        subtitle.pack()
        
        # Create a frame for the list
        list_frame = tk.Frame(dialog)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Create a treeview for inactive students
        columns = ('student_id', 'name', 'last_attendance', 'days_inactive', 'email')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        tree.heading('student_id', text='Student ID')
        tree.heading('name', text='Name')
        tree.heading('last_attendance', text='Last Attendance')
        tree.heading('days_inactive', text='Days Inactive')
        tree.heading('email', text='Email')
        
        tree.column('student_id', width=100)
        tree.column('name', width=150)
        tree.column('last_attendance', width=120)
        tree.column('days_inactive', width=100)
        tree.column('email', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Add students to treeview
        for student in inactive_students:
            last_attendance = student['last_attendance'].strftime('%Y-%m-%d') if student['last_attendance'] else 'Never'
            days_inactive = str(student['days_inactive'])
            
            tree.insert('', 'end', values=(
                student['student_id'],
                student['name'],
                last_attendance,
                days_inactive,
                student['email']
            ))
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # Send warnings button
        send_btn = tk.Button(button_frame, text="📧 Send Warning Emails", 
                            font=("Arial", 10, "bold"), fg="white", bg="#e74c3c",
                            width=20, command=lambda: self.send_warning_emails(inactive_students, dialog))
        send_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", 
                             font=("Arial", 10), width=15,
                             command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_label = tk.Label(dialog, text=f"Total inactive students: {len(inactive_students)}", 
                             font=("Arial", 9))
        info_label.pack(pady=5)
    
    def send_warning_emails(self, inactive_students, dialog):
        """Send warning emails to inactive students"""
        if not inactive_students:
            return
        
        # Check if email is configured
        if self.email_sender == "your-email@gmail.com" or not self.email_password:
            messagebox.showerror("Email Not Configured", 
                               "Please configure email settings first!\n\n"
                               "1. Click 'Email Settings' button\n"
                               "2. Enter your Gmail address\n"
                               "3. Generate an App Password in your Google Account\n"
                               "4. Enter the App Password")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Send", 
                                     f"Send warning emails to {len(inactive_students)} inactive students?\n\n"
                                     "This will send personalized warnings to each student's Gsuite account.")
        
        if not confirm:
            return
        
        # Track success/failure
        successful = []
        failed = []
        
        # Send emails
        for student in inactive_students:
            try:
                self.send_warning_email(student)
                successful.append(student['student_id'])
            except Exception as e:
                failed.append(f"{student['student_id']}: {str(e)}")
        
        # Show results
        result_message = ""
        if successful:
            result_message += f"✅ Successfully sent to {len(successful)} students\n"
        
        if failed:
            result_message += f"\n❌ Failed to send to {len(failed)} students:\n"
            for fail in failed:
                result_message += f"  - {fail}\n"
        
        messagebox.showinfo("Email Results", result_message)
        
        # Close the dialog if all emails sent successfully
        if not failed:
            dialog.destroy()
    
    def send_warning_email(self, student):
        """Send a warning email to a specific student"""
        # Email content
        subject = f"⚠️ Attendance Warning: {student['name']} ({student['student_id']})"
        
        if student['last_attendance']:
            last_date = student['last_attendance'].strftime('%B %d, %Y')
            body = f"""
Dear {student['name']},

This is an automated warning regarding your attendance record.

You have been marked as INACTIVE for {student['days_inactive']} days.
Your last recorded attendance was on: {last_date}

Please ensure you attend classes regularly and use the attendance QR code 
to mark your presence in future sessions.

Failure to maintain regular attendance may affect your academic standing.

If you believe this is an error, please contact your professor immediately.

Best regards,
Attendify System
            """
        else:
            body = f"""
Dear {student['name']},

This is an automated warning regarding your attendance record.

You have NOT recorded any attendance since the beginning of the semester.
Please ensure you attend classes regularly and use the attendance QR code 
to mark your presence in future sessions.

Consistent lack of attendance may affect your academic standing.

If you believe this is an error, please contact your professor immediately.

Best regards,
Attendify System
            """
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = student['email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Warning email sent to {student['email']}")
        except Exception as e:
            print(f"❌ Failed to send email to {student['email']}: {str(e)}")
            raise
    
    def configure_email_settings(self):
        """Configure email settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Email Configuration")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        tk.Label(dialog, text="📧 Email Configuration", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Email sender
        tk.Label(form_frame, text="Your Gmail Address:", 
                font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        email_entry = tk.Entry(form_frame, width=35)
        email_entry.grid(row=0, column=1, pady=10, padx=10)
        email_entry.insert(0, self.email_sender)
        
        # App Password
        tk.Label(form_frame, text="Gmail App Password:", 
                font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        password_entry = tk.Entry(form_frame, width=35, show="*")
        password_entry.grid(row=1, column=1, pady=10, padx=10)
        password_entry.insert(0, self.email_password)
        
        # Instructions
        instructions_frame = tk.LabelFrame(dialog, text="How to get App Password", padx=10, pady=10)
        instructions_frame.pack(pady=10, padx=20, fill=tk.X)
        
        instructions = [
            "1. Go to your Google Account",
            "2. Click 'Security'",
            "3. Under 'Signing in to Google', click 'App passwords'",
            "4. Generate a new app password for 'Mail'",
            "5. Copy the 16-character password and paste it above",
            "Note: Use App Password, NOT your regular password!"
        ]
        
        for i, instruction in enumerate(instructions):
            tk.Label(instructions_frame, text=instruction, 
                    font=("Arial", 8), justify=tk.LEFT).pack(anchor=tk.W)
        
        # Test email frame
        test_frame = tk.Frame(dialog)
        test_frame.pack(pady=10)
        
        test_email_entry = tk.Entry(test_frame, width=25)
        test_email_entry.pack(side=tk.LEFT, padx=5)
        test_email_entry.insert(0, "test@example.com")
        
        test_btn = tk.Button(test_frame, text="Test Email", 
                           command=lambda: self.test_email_config(
                               email_entry.get(), 
                               password_entry.get(), 
                               test_email_entry.get()
                           ))
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_config():
            self.email_sender = email_entry.get()
            self.email_password = password_entry.get()
            messagebox.showinfo("Success", "Email configuration saved!")
            dialog.destroy()
        
        save_btn = tk.Button(button_frame, text="Save Configuration", 
                           font=("Arial", 10, "bold"), bg="#2ecc71", fg="white",
                           command=save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                             command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def test_email_config(self, sender, password, test_email):
        """Test email configuration"""
        if not sender or not password or not test_email:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        try:
            # Test SMTP connection
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            
            # Send test email
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = test_email
            msg['Subject'] = "Test Email from Attendify"
            
            body = "This is a test email from Attendify System.\n\nIf you received this, email configuration is working correctly!"
            msg.attach(MIMEText(body, 'plain'))
            
            server.send_message(msg)
            server.quit()
            
            messagebox.showinfo("Success", f"Test email sent successfully to {test_email}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email:\n\n{str(e)}")

    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_flask():
            try:
                from app import app  # Import your Flask app
                print("🚀 Starting Flask web server on http://localhost:5000")
                app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
            except Exception as e:
                print(f"❌ Flask server error: {e}")
        
        # Start Flask in a daemon thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Wait a moment for server to start, then open browser
        self.root.after(2000, self.open_browser)
    
    def open_browser(self):
        """Open web browser to the Flask app"""
        try:
            webbrowser.open('http://localhost:5000')
            print("🌐 Browser opened to http://localhost:5000")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")

    def generate_qr_code(self):
        """Generate QR code for attendance"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Attendance QR Code")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Generate Attendance QR Code", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Course selection
        ttk.Label(form_frame, text="Course Code:").grid(row=1, column=0, sticky=tk.W, pady=8)
        course_combo = ttk.Combobox(form_frame, width=20)
        course_combo.grid(row=1, column=1, pady=8, padx=(10, 0))
        
        courses = self.get_all_courses()
        course_combo['values'] = courses
        if courses:
            course_combo.set(courses[0])
        
        ttk.Label(form_frame, text="Course Title:").grid(row=2, column=0, sticky=tk.W, pady=8)
        course_title_entry = ttk.Combobox(form_frame, width=20)
        course_title_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
        course_title_entry['values'] = ["Discrete Mathematics", "Advanced Computer Programming", 
                                       "Object Oriented Programming", "Computer Networking 1", 
                                       "Calculus-Based Physics", "Asean Literature", 
                                       "PathFit-3", "Database Management Systems"]
        if course_title_entry['values']:
            course_title_entry.set(course_title_entry['values'][0])
        
        ttk.Label(form_frame, text="Class Time:").grid(row=3, column=0, sticky=tk.W, pady=8)
        class_time_entry = ttk.Entry(form_frame, width=20)
        class_time_entry.grid(row=3, column=1, pady=8, padx=(10, 0))
        class_time_entry.insert(0, "MWF 8:00-9:00 AM")  # Default
        
        def generate_and_display():
            course_code = course_combo.get().strip()
            course_title = course_title_entry.get().strip()
            class_time = class_time_entry.get().strip()
            section = self.current_section.get().strip()
            
            if not all([course_code, course_title, class_time, section]):
                messagebox.showerror("Error", "Please fill in all fields!")
                return
            
            # Generate QR code with proper URL that includes parameters
            qr_url = "http://192.168.1.6:5000"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Ensure qr_codes directory exists
            os.makedirs('qr_codes', exist_ok=True)
            
            # Save QR code
            filename = f"qr_codes/{course_code}_{section}_attendance.png"
            qr_image.save(filename)
            
            # Store QR code info for later viewing
            self.last_generated_qr = {
                'filename': filename,
                'course_code': course_code,
                'course_title': course_title,
                'class_time': class_time,
                'section': section,
                'url': qr_url
            }
            
            # Display QR code in the main window
            self.display_qr_code(filename, course_code, course_title, class_time, section)
            
            messagebox.showinfo("Success", f"QR Code generated!\n\nCourse: {course_code}\nSection: {section}\nSaved as: {filename}")
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Generate QR Code", 
                  command=generate_and_display).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def see_generated_qr(self):
        """Display the last generated QR code in a large popup window"""
        if not self.last_generated_qr:
            messagebox.showinfo("Info", "No QR code has been generated yet. Please generate one first.")
            return
        
        # Create a new popup window for large QR code display
        popup = tk.Toplevel(self.root)
        popup.title("QR Code - Large View")
        popup.geometry("600x700")
        popup.configure(bg="pink")
        popup.transient(self.root)
        popup.grab_set()
        
        # Center the popup on the main window
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Get QR code data
        filename = self.last_generated_qr['filename']
        course_code = self.last_generated_qr['course_code']
        course_title = self.last_generated_qr['course_title']
        class_time = self.last_generated_qr['class_time']
        section = self.last_generated_qr['section']
        qr_url = self.last_generated_qr['url']
        
        # Title
        title_label = tk.Label(popup, text="ATTENDANCE QR CODE", 
                              font=("Arial", 16, "bold"), bg="pink")
        title_label.pack(pady=20)
        
        # Course information frame
        info_frame = tk.Frame(popup, bg="pink")
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Course: {course_code} - {course_title}", 
                 font=("Arial", 12, "bold"), bg="pink").pack()
        tk.Label(info_frame, text=f"Section: {section}", 
                 font=("Arial", 12), bg="pink").pack()
        tk.Label(info_frame, text=f"Class Time: {class_time}", 
                 font=("Arial", 12), bg="pink").pack()
        
        # Large QR code display frame
        qr_display_frame = tk.LabelFrame(popup, text="Scan QR Code for Attendance", 
                                        font=("Arial", 12, "bold"), bg="pink", 
                                        padx=20, pady=20)
        qr_display_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        try:
            # Load and display large QR code image
            image = Image.open(filename)
            # Resize to larger size for the popup
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create label for QR code
            qr_label = tk.Label(qr_display_frame, image=photo, bg="white")
            qr_label.image = photo  # Keep a reference
            qr_label.pack(pady=10)
            
            # URL information
            url_label = tk.Label(qr_display_frame, 
                                text="Scan this QR code with your phone camera\nor any QR code scanner app",
                                font=("Arial", 10), bg="pink", justify=tk.CENTER)
            url_label.pack(pady=5)
            
            url_link = tk.Label(qr_display_frame, 
                               text= "http://192.168.1.6:5000",
                               font=("Arial", 9, "bold"), fg="blue", 
                               bg="pink", cursor="hand2")
            url_link.pack(pady=5)
            
            def open_url(event):
                webbrowser.open('http://192.168.1.6:5000')
            
            url_link.bind("<Button-1>", open_url)
            
        except Exception as e:
            error_label = tk.Label(qr_display_frame, 
                                  text=f"Error loading QR code:\n{str(e)}",
                                  font=("Arial", 10), fg="red", bg="pink")
            error_label.pack(pady=20)
        
        # Instructions frame
        instructions_frame = tk.Frame(popup, bg="pink")
        instructions_frame.pack(pady=10)
        
        instructions = [
            "📱 How to use:",
            "1. Students scan this QR code with their phone camera",
            "2. They will be directed to the attendance page",
            "3. Students enter their Student ID to mark attendance",
            "4. Attendance is recorded automatically"
        ]
        
        for instruction in instructions:
            tk.Label(instructions_frame, text=instruction, 
                    font=("Arial", 9), bg="pink", justify=tk.LEFT).pack(anchor="w")
        
        # Close button
        close_button = tk.Button(popup, text="Close", font=("Arial", 10, "bold"), 
                                fg="black", bg="silver", width=15,
                                command=popup.destroy)
        close_button.pack(pady=20)
        
        # Also update the small QR code in the main window
        self.display_qr_code(filename, course_code, course_title, class_time, section)

    def display_qr_code(self, filename, course_code, course_title, class_time, section):
        """Display the generated QR code in the main window"""
        try:
            # Load and display QR code image
            image = Image.open(filename)
            # Resize to fit the square frame (250x250)
            image = image.resize((240, 240), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update QR code label with image
            self.qr_label.configure(image=photo, text="")
            self.qr_label.image = photo  # Keep a reference
            
            # Add course info below QR code
            info_text = f"Course: {course_code}\nSection: {section}\nTime: {class_time}"
            self.qr_info_label.config(text=info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not display QR code: {str(e)}")

    def get_all_courses(self):
        """Get all unique courses from database"""
        try:
            conn = sqlite3.connect('attendify.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT course FROM students WHERE course IS NOT NULL ORDER BY course")
            courses = [row[0] for row in cursor.fetchall() if row[0]]
            conn.close()
            return courses
        except:
            return ["CPE405", "IT2104", "CS201"]  # Fallback

    def load_sections(self):
        """Load all available sections from database as suggestions"""
        try:
            sections = Student.get_all_sections()
            self.section_combo['values'] = sections  # These are now SUGGESTIONS, not limits
            
            if sections:
                self.current_section.set(sections[0])
                self.on_section_change()
            else:
                # No sections yet - clear everything
                self.current_section.set("")
                self.stats_label.config(text="No sections found. Add students first.")
                self.refresh_student_list()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading sections: {str(e)}")
    
    def on_section_type(self, event=None):
        """When professor types in section box, update display"""
        # Only update if we have a non-empty section
        if self.current_section.get().strip():
            self.on_section_change()
    
    def on_section_change(self, event=None):
        """When section is changed (selected or typed), update the display"""
        section = self.current_section.get().strip()
        if section:
            self.update_section_stats(section)
            self.refresh_student_list()
    
    def update_section_stats(self, section):
        """Update statistics for selected section"""
        if not section:
            self.stats_label.config(text="Please select or type a section")
            return
    
        # Get student count
        student_count = Student.get_student_count_by_section(section)
    
        # Get today's attendance count
        attendance_today = Attendance.get_todays_attendance_by_section(section)
    
        # Get course-specific attendance if QR code was generated
        qr_course = ""
        if self.last_generated_qr:
            qr_course = self.last_generated_qr.get('course_code', '')
        
        course_attendance = 0
        if qr_course:
            course_attendance = Attendance.get_todays_attendance_by_section(section, qr_course)
    
        stats_text = f"📊 Section: {section}\n"
        stats_text += f"👥 Total Students: {student_count}\n"
        stats_text += f"✅ Today's Total Attendance: {attendance_today}/{student_count}\n"
    
        if qr_course:
            stats_text += f"📚 For {qr_course}: {course_attendance}/{student_count}\n"
    
        # Add percentage
        if student_count > 0:
            percentage = (attendance_today / student_count * 100) if student_count > 0 else 0
            stats_text += f"📈 Overall Rate: {percentage:.1f}%"
    
        self.stats_label.config(text=stats_text)
    
    def refresh_student_list(self):
        """Refresh student list for current section with attendance status"""
        section = self.current_section.get().strip()
        if not section:
            # Clear the treeview if no section selected
            for item in self.tree_view.get_children():
                self.tree_view.delete(item)
            return
        
        # Get current course from QR code if available
        current_course = ""
        if self.last_generated_qr:
            current_course = self.last_generated_qr.get('course_code', '')
    
        # Clear existing items
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
    
        # Get students for current section
        students = Student.get_students_by_section(section)
    
        # Get today's attendance records
        today = datetime.now().date()
        attendance_records = Attendance.get_attendance_records_by_section(section, today)
    
        # Create a set of student IDs who have attended today
        attended_students = set()
        for record in attendance_records:
            if len(record) > 1:  # Check if record has student_id
                attended_students.add(record[1])  # student_id is at index 1
    
        # Add students to treeview
        for student in students:
            # Safe way to access student data
            student_id = student[1] if len(student) > 1 else "N/A"
            name = student[2] if len(student) > 2 else "N/A"
            course = student[3] if len(student) > 3 else "N/A"
            block = student[5] if len(student) > 5 else "N/A"
            gsuite = student[6] if len(student) > 6 else "N/A"
        
            # Check attendance status
            if student_id in attended_students:
                status = "✅ Present"
            else:
                status = "❌ Absent"
                
            # Insert the student into treeview
            self.tree_view.insert('', 'end', values=(status, student_id, name, course, block, gsuite))
        
        # Apply colors
        self.apply_attendance_colors()
        
    def refresh_attendance_status(self):
        """Refresh the attendance status display"""
        section = self.current_section.get().strip()
        if not section:
            messagebox.showinfo("Info", "Please select a section first")
            return
    
        self.refresh_student_list()
        self.update_section_stats(section)
    
        # Update timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Last update: {current_time}")
        
    def debug_current_section(self):
        """Debug method to check current section"""
        print(f"Current section: {self.current_section.get()}")
        print(f"Section combo values: {self.section_combo['values']}")
        return self.current_section.get()


if __name__ == "__main__":
    # Initialize database
    from database import init_db
    init_db()
    
    root = tk.Tk()
    app = ProfessorApp(root)
    root.mainloop()