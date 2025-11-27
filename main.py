import threading
import tkinter as tk
from tkinter import ttk, messagebox
from models import Student
import qrcode
import os
import sqlite3
from PIL import Image, ImageTk
import webbrowser
from app import app 

class ProfessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendify - Professor System")
        self.root.geometry("1100x700")  # Increased width for QR code
        
        # Current section state
        self.current_section = tk.StringVar()
        
        self.create_widgets()
        self.load_sections()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(header_frame, text="🎯 ATTENDIFY PROFESSOR SYSTEM", 
                 font=("Arial", 18, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        # Section Selection
        self.section_frame = ttk.LabelFrame(main_frame, text="Section Management", padding="15")
        self.section_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(self.section_frame, text="Section:").grid(row=0, column=0, sticky=tk.W)
        
        self.section_combo = ttk.Combobox(self.section_frame, textvariable=self.current_section, 
                                         width=15)
        self.section_combo.grid(row=0, column=1, padx=(10, 0))
        self.section_combo.bind('<<ComboboxSelected>>', self.on_section_change)
        self.section_combo.bind('<KeyRelease>', self.on_section_type)
        
        ttk.Button(self.section_frame, text="Refresh Sections", 
                  command=self.load_sections).grid(row=0, column=2, padx=(10, 0))
        
        # NEW: QR Code Generator Button
        ttk.Button(self.section_frame, text="📱 Generate QR Code", 
                  command=self.generate_qr_code).grid(row=0, column=3, padx=(10, 0))
        
        ttk.Button(self.section_frame, text="Add Student to Section", 
                  command=self.open_add_student).grid(row=1, column=0, columnspan=4, pady=(10, 0))
        
        # Section Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Section Statistics", padding="15")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0), padx=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="Please select or type a section")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # QR Code Display Area (NEW)
        self.qr_frame = ttk.LabelFrame(main_frame, text="QR Code", padding="15")
        self.qr_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0), padx=(10, 0))
        
        self.qr_label = ttk.Label(self.qr_frame, text="Click 'Generate QR Code' to create attendance QR")
        self.qr_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Student List Area
        list_frame = ttk.LabelFrame(main_frame, text="Student Management", padding="15")
        list_frame.grid(row=1, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create a treeview for student list
        columns = ("ID", "Name", "Course", "Block", "GSuite")
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        self.student_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons for students
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="Refresh Students", 
                  command=self.refresh_student_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Edit Selected", 
                  command=self.edit_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_student).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.qr_frame.columnconfigure(0, weight=1)
        self.qr_frame.rowconfigure(0, weight=1)
    

        self.load_sections()
        self.start_flask_server()  # Start Flask when app starts
    
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
        
        # Get unique courses from students
        courses = self.get_all_courses()
        course_combo['values'] = courses
        if courses:
            course_combo.set(courses[0])
        
        ttk.Label(form_frame, text="Course Title:").grid(row=2, column=0, sticky=tk.W, pady=8)
        course_title_entry = ttk.Entry(form_frame, width=20)
        course_title_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
        course_title_entry.insert(0, "Discrete Mathematics")  # Default
        
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
            
            # Generate QR code
            qr_url = "http://192.168.1.8:5000"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Ensure qr_codes directory exists
            os.makedirs('qr_codes', exist_ok=True)
            
            # Save QR code
            filename = f"qr_codes/{course_code}_{section}_attendance.png"
            qr_image.save(filename)
            
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

    def display_qr_code(self, filename, course_code, course_title, class_time, section):
        """Display the generated QR code in the main window"""
        try:
            # Load and display QR code image
            image = Image.open(filename)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update QR code label with image
            self.qr_label.configure(image=photo, text="")
            self.qr_label.image = photo  # Keep a reference
            
            # Add course info below QR code
            info_text = f"Course: {course_code}\nSection: {section}\nTime: {class_time}"
            info_label = ttk.Label(self.qr_frame, text=info_text, justify=tk.CENTER)
            info_label.grid(row=1, column=0, pady=(10, 0))
            
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
        
        student_count = Student.get_student_count_by_section(section)
        
        stats_text = f"Section: {section}\n"
        stats_text += f"Total Students: {student_count}\n"
        stats_text += f"Today's Attendance: 0/{student_count}"  # We'll implement this later
        
        self.stats_label.config(text=stats_text)
    
    def refresh_student_list(self):
        """Refresh student list for current section"""
        section = self.current_section.get().strip()
        if not section:
            # Clear the treeview if no section selected
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            return
        
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Get students for current section
        students = Student.get_students_by_section(section)
        
        # Add students to treeview with safe data access
        for student in students:
            # Safe way to access student data - handle cases where some fields might be missing
            student_id = student[1] if len(student) > 1 else "N/A"
            name = student[2] if len(student) > 2 else "N/A"
            course = student[3] if len(student) > 3 else "N/A"
            block = student[5] if len(student) > 5 else "N/A"  # section is at index 4
            gsuite = student[6] if len(student) > 6 else "N/A"
            
            self.student_tree.insert('', 'end', values=(student_id, name, course, block, gsuite))
    
    def open_add_student(self):
        """Open dialog to add new student to current section"""
        section = self.current_section.get().strip()
        if not section:
            messagebox.showwarning("Warning", "Please enter or select a section first!")
            return
        
        self.create_add_student_dialog(section)
    
    def create_add_student_dialog(self, section):
        """Create dialog for adding new student"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Student to {section}")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text=f"Add Student to {section}", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Form fields
        ttk.Label(form_frame, text="Student ID:").grid(row=1, column=0, sticky=tk.W, pady=8)
        student_id_entry = ttk.Entry(form_frame, width=25)
        student_id_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
        
        ttk.Label(form_frame, text="Full Name:").grid(row=2, column=0, sticky=tk.W, pady=8)
        name_entry = ttk.Entry(form_frame, width=25)
        name_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
        
        ttk.Label(form_frame, text="Course:").grid(row=3, column=0, sticky=tk.W, pady=8)
        course_entry = ttk.Entry(form_frame, width=25)
        course_entry.grid(row=3, column=1, pady=8, padx=(10, 0))
        
        ttk.Label(form_frame, text="Section:").grid(row=4, column=0, sticky=tk.W, pady=8)
        section_label = ttk.Label(form_frame, text=section, font=("Arial", 9, "bold"))
        section_label.grid(row=4, column=1, sticky=tk.W, pady=8, padx=(10, 0))
        
        ttk.Label(form_frame, text="Block:").grid(row=5, column=0, sticky=tk.W, pady=8)
        block_entry = ttk.Entry(form_frame, width=25)
        block_entry.grid(row=5, column=1, pady=8, padx=(10, 0))
        
        ttk.Label(form_frame, text="GSuite Email:").grid(row=6, column=0, sticky=tk.W, pady=8)
        gsuite_entry = ttk.Entry(form_frame, width=25)
        gsuite_entry.grid(row=6, column=1, pady=8, padx=(10, 0))
        
        def save_student():
            # Get data from form
            student_data = {
                'student_id': student_id_entry.get().strip(),
                'name': name_entry.get().strip(),
                'course': course_entry.get().strip(),
                'section': section,  # Use the current section
                'block': block_entry.get().strip(),
                'gsuite': gsuite_entry.get().strip()
            }
            
            # Validate
            if not all(student_data.values()):
                messagebox.showerror("Error", "Please fill in all fields!")
                return
            
            # Save student
            success, message = Student.create(student_data)
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.refresh_student_list()
                self.load_sections()  # Refresh section list
            else:
                messagebox.showerror("Error", message)
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Save Student", 
                  command=save_student).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def edit_student(self):
        """Edit selected student - placeholder for now"""
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to edit!")
            return
        messagebox.showinfo("Info", "Edit feature coming soon!")
    
    def delete_student(self):
        """Delete selected student - placeholder for now"""
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to delete!")
            return
        messagebox.showinfo("Info", "Delete feature coming soon!")

if __name__ == "__main__":
    # Initialize database
    from database import init_db
    init_db()
    
    root = tk.Tk()
    app = ProfessorApp(root)
    root.mainloop()