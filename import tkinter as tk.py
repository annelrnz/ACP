import tkinter as tk
from tkinter import messagebox

# Conceptual data store for absences (e.g., a dictionary where keys are student IDs)
# This data would need to be updated and managed based on your full application logic
student_absences = {"student_id_123": 3} # Example student with 3 absences

def record_absence(student_id):
    """Function to record an absence and check for the warning condition."""
    global student_absences
    
    # Check if student is in the record, if not, add them
    if student_id not in student_absences:
        student_absences[student_id] = 0
    
    # Increment the absence count
    student_absences[student_id] += 1
    current_absences = student_absences[student_id]
    
    print(f"Student {student_id} now has {current_absences} absences this week.")

    # Check if the absence count exceeds the threshold (3 absences)
    if current_absences > 3:
        # Display the warning message box
        title = "Absence Alert!"
        message = f"Student {student_id} has exceeded the limit of 3 absences this week! Total: {current_absences}."
        
        # This line creates and displays the warning window
        messagebox.showwarning(title, message)

# --- Tkinter GUI Setup (Example) ---

root = tk.Tk()
root.title("Attendance Tracker")
root.geometry("300x150")

# Optional: if you only want the pop-up and not the main window, you can hide the root
# root.withdraw()

label = tk.Label(root, text="Click to record an absence for student_id_123")
label.pack(pady=10)

# Button to trigger the absence recording and check
# The lambda function is used to pass the student ID argument to the function
absence_button = tk.Button(root, text="Mark Absent", command=lambda: record_absence("student_id_123"))
absence_button.pack(pady=10)

# A button to show the current counts
check_button = tk.Button(root, text="Check Absences", command=lambda: print(student_absences))
check_button.pack(pady=10)

root.mainloop()
