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
        self.root.title("Attendify: Mark Your Presence")
        self.root.geometry("1200x750")  # Slightly larger to accommodate all elements
        
        # Apply pink background
        bg_color = "pink"
        self.root.configure(bg=bg_color)
        self.root.resizable(False, False)
        
        # Current section state
        self.current_section = tk.StringVar()
        self.last_generated_qr = None  # Track last generated QR code
        
        # Initialize QR code labels
        self.qr_label = None
        self.qr_info_label = None
        
        self.create_widgets()
        self.load_sections()
    
    def create_widgets(self):
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1) 
        self.root.grid_columnconfigure(1, weight=1) 
        self.root.grid_rowconfigure(2, weight=1)

        # Entry Frame (Left Side)
        entry_frame = tk.Frame(self.root, bg="pink", padx=10, pady=10)
        entry_frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(entry_frame, text="Enter Student Details:", font=("Arial", 12, "bold"), bg="pink").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        tk.Label(entry_frame, text="Student ID:", bg="pink").grid(row=1, column=0, sticky="w")
        self.entry_id = tk.Entry(entry_frame, width=30)
        self.entry_id.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(entry_frame, text="Name:", bg="pink").grid(row=2, column=0, sticky="w")
        self.entry_name = tk.Entry(entry_frame, width=30)
        self.entry_name.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(entry_frame, text="Program:", bg="pink").grid(row=3, column=0, sticky="w")
        self.entry_program = tk.Entry(entry_frame, width=30)
        self.entry_program.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(entry_frame, text="Block:", bg="pink").grid(row=4, column=0, sticky="w")
        self.entry_block = tk.Entry(entry_frame, width=30)
        self.entry_block.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(entry_frame, text="Gsuite Account:", bg="pink").grid(row=5, column=0, sticky="w")
        self.entry_gsuite = tk.Entry(entry_frame, width=30)
        self.entry_gsuite.grid(row=5, column=1, pady=5, sticky="ew")

        entry_frame.grid_columnconfigure(1, weight=1)

        # Button Frame (Right Side - Top)
        button_frame = tk.Frame(self.root, bg="pink", padx=10, pady=10)
        button_frame.grid(row=0, column=1, sticky="we")

        # Section Management
        tk.Label(button_frame, text="Section Management:", font=("Arial", 12, "bold"), bg="pink").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        tk.Label(button_frame, text="Section:", bg="pink").grid(row=1, column=0, sticky="w")
        self.section_combo = ttk.Combobox(button_frame, textvariable=self.current_section, width=15)
        self.section_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.section_combo.bind('<<ComboboxSelected>>', self.on_section_change)
        self.section_combo.bind('<KeyRelease>', self.on_section_type)

        # Action Buttons with silver background
        tk.Button(button_frame, text="ADD", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=self.add_student).grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        tk.Button(button_frame, text="UPDATE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=self.update_student).grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        tk.Button(button_frame, text="VIEW", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=self.view_records).grid(row=3, column=0, pady=5, padx=5, sticky="ew")
        tk.Button(button_frame, text="DELETE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=self.delete_student).grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        
        # Additional buttons
        tk.Button(button_frame, text="Refresh Sections", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=self.load_sections).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        tk.Button(button_frame, text="Generate QR Code", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=self.generate_qr_code).grid(row=5, column=0, pady=5, sticky="ew")
        tk.Button(button_frame, text="See QR Code", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=self.see_generated_qr).grid(row=5, column=1, pady=5, padx=(5, 0), sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Title Label
        tk.Label(self.root, text="Student Record", font=("Arial", 20, "bold"), bg="pink").grid(row=1, column=0, columnspan=1, pady=(20, 5))

        # Middle Section - Statistics and QR Code
        middle_frame = tk.Frame(self.root, bg="pink", padx=10, pady=10)
        middle_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        # Configure middle frame grid - give more space to QR code
        middle_frame.columnconfigure(0, weight=2)  # Less space for statistics
        middle_frame.columnconfigure(1, weight=3)  # More space for QR code
        middle_frame.rowconfigure(0, weight=1)

        # Section Statistics (Left side of middle frame)
        stats_frame = tk.LabelFrame(middle_frame, text="Section Statistics", font=("Arial", 10, "bold"), bg="pink", padx=10, pady=10)
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.stats_label = tk.Label(stats_frame, text="Please select or type a section", font=("Arial", 11), bg="pink", justify=tk.LEFT)
        self.stats_label.pack(expand=True, fill=tk.BOTH)

        # QR Code Frame (Right side of middle frame)
        qr_frame = tk.LabelFrame(middle_frame, text="QR Code", font=("Arial", 10, "bold"), bg="pink", padx=10, pady=10)
        qr_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Initialize QR code label
        self.qr_label = tk.Label(qr_frame, text="Generate QR Code first", font=("Arial", 10), 
                                bg="white", width=30, height=10, relief="solid")
        self.qr_label.pack(pady=10)
        
        # QR code info label
        self.qr_info_label = tk.Label(qr_frame, text="", font=("Arial", 9), bg="pink", justify=tk.CENTER)
        self.qr_info_label.pack(pady=5)
        
        # Bottom Section - Student Records Treeview
        bottom_frame = tk.Frame(self.root, bg="pink", padx=10, pady=10)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        # Treeview for student records
        columns = ('student_id', 'name', 'program', 'block', 'gsuite_account')
        self.tree_view = ttk.Treeview(bottom_frame, columns=columns, show='headings', height=12)
        self.tree_view.grid(row=0, column=0, sticky="nsew")

        # Configure column headings and widths
        self.tree_view.heading('student_id', text='Student ID')
        self.tree_view.heading('name', text='Name')
        self.tree_view.heading('program', text='Program')
        self.tree_view.heading('block', text='Block')
        self.tree_view.heading('gsuite_account', text='Gsuite Account')

        # To adjust the sizes ng mga columns
        self.tree_view.column('student_id', anchor=tk.CENTER, width=100)
        self.tree_view.column('name', anchor=tk.W, width=150)
        self.tree_view.column('program', anchor=tk.W, width=100)
        self.tree_view.column('block', anchor=tk.CENTER, width=80)
        self.tree_view.column('gsuite_account', anchor=tk.W, width=150)

        # Add a scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        self.tree_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Configure grid weights for bottom frame
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.rowconfigure(0, weight=1)

        self.load_sections()
        self.start_flask_server()

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
            self.refresh_student_list()
            self.load_sections()
        else:
            messagebox.showerror("Error", message)

    def view_records(self):
        """Displays all current student records in the Treeview format."""
        self.refresh_student_list()

    def update_student(self):
        """Updates an existing student record based on the Student ID."""
        student_id = self.entry_id.get()
        if not student_id:
            messagebox.showerror("Error!", "Student ID cannot be empty for update.")
            return

        # Update logic would go here - placeholder for now
        messagebox.showinfo("Info", "Update feature will be implemented fully with database integration")

    def delete_student(self):
        """Deletes a student record based on the Student ID."""
        student_id = self.entry_id.get()
        if not student_id:
            messagebox.showerror("Error", "Student ID cannot be empty for deletion.")
            return

        # Delete logic would go here - placeholder for now
        messagebox.showinfo("Info", "Delete feature will be implemented fully with database integration")

    def clear_entries(self):
        """Helper function to clear all input fields."""
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_program.delete(0, tk.END)
        self.entry_block.delete(0, tk.END)
        self.entry_gsuite.delete(0, tk.END)

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
        course_title_entry.insert(0, "Discrete Mathematics") 
        course_title_entry.insert(1, "Advanced Computer Programming") 
        course_title_entry.insert(2, "Object Oriented Programming") 
        course_title_entry.insert(3, "Computer Networking 1") 
        course_title_entry.insert(4, "Calculus-Based Physics") 
        course_title_entry.insert(5, "Asean Literature")
        course_title_entry.insert(6, "PathFit-3")  
        course_title_entry.insert(7, "Database Management Systems") 
        
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
            
            # Create QR code image
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
            for item in self.tree_view.get_children():
                self.tree_view.delete(item)
            return
        
        # Clear existing items
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
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
            
            self.tree_view.insert('', 'end', values=(student_id, name, course, block, gsuite))

if __name__ == "__main__":
    # Initialize database
    from database import init_db
    init_db()
    
    root = tk.Tk()
    app = ProfessorApp(root)
    root.mainloop()