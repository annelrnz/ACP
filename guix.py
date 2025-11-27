import tkinter as tk
from tkinter import messagebox
import sqlite3

class AttendanceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Attendance")

        # Gawa ng connection sa database
        self.conn = sqlite3.connect('attendance.db')
        self.cursor = self.conn.cursor()

        # G, C, P
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                student_id TEXT,
                name TEXT,
                date TEXT,
                status TEXT
            )
        ''')

        # Gawa ng GUI components
        tk.Label(self.root, text="Student ID:").grid(row=0, column=0)
        self.student_id_entry = tk.Entry(self.root)
        self.student_id_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Name:").grid(row=1, column=0)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Date (YYYY-MM-DD):").grid(row=2, column=0)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Status:").grid(row=3, column=0)
        self.status_var = tk.StringVar()
        self.status_var.set("Present")
        self.status_option = tk.OptionMenu(self.root, self.status_var, "Present", "Absent")
        self.status_option.grid(row=3, column=1)

        tk.Button(self.root, text="Submit", command=self.submit_attendance).grid(row=4, column=1)

        tk.Label(self.root, text="Search Student ID:").grid(row=5, column=0)
        self.search_entry = tk.Entry(self.root)
        self.search_entry.grid(row=5, column=1)

        tk.Button(self.root, text="Search", command=self.search_attendance).grid(row=6, column=1)

        tk.Label(self.root, text="Enter Student ID to Delete:").grid(row=7, column=0)
        self.delete_entry = tk.Entry(self.root)
        self.delete_entry.grid(row=7, column=1)

        tk.Button(self.root, text="Delete", command=self.delete_attendance).grid(row=8, column=1)

    def submit_attendance(self):
        student_id = self.student_id_entry.get()
        name = self.name_entry.get()
        date = self.date_entry.get()
        status = self.status_var.get()

        self.cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (student_id, name, date, status))
        self.conn.commit()

        messagebox.showinfo("Success", "Attendance record submitted successfully")

    def search_attendance(self):
        student_id = self.search_entry.get()

        self.cursor.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
        records = self.cursor.fetchall()

        absences = 0
        for record in records:
            if record[3] == 'Absent':
                absences += 1

        if absences >= 3:
            messagebox.showwarning("Warning", "Student has reached maximum absences!")
        else:
            messagebox.showinfo("Attendance", "Student is present 4-6 days a week")

    def delete_attendance(self):
        student_id = self.delete_entry.get()

        self.cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        self.conn.commit()

        messagebox.showinfo("Success", "Attendance record deleted successfully")

    def run(self):
        self.root.mainloop()

if __name__ == "_main_":
    attendance_system = AttendanceSystem()
    attendance_system.run()