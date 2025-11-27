import tkinter as tk

# Function for the button action
def submit_name():
    student_name = name_entry.get()
    print("Student Name Entered:", student_name)

# Create the main window
root = tk.Tk()
 
# Set title and size
root.title("CICS Management System")
root.geometry("1500x600")  # width x height

# Make the window not resizable
root.resizable(False, False)

# Change the background color
root.configure(bg="pink")  # light beige color

# ---- Title Label ----
title_label = tk.Label(
    root,
    text="Student Information Management System",
    font=("Arial", 24, "bold"),
    fg="black",
    bg="white"
)
title_label.pack(pady=20)

# ---- Student Name Label ----
name_label = tk.Label(
    root,
    text="Student Name:",
    font=("Times New Roman", 16),
    fg="black",
    bg="#efdecd"
)
name_label.pack(pady=10, anchor="w", padx=10)

# ---- Text Box (Entry) ----
name_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=20
)
name_entry.pack(pady=5, padx=10, anchor="w")

# ---- Button ----
submit_button = tk.Button(
    root,
    text="Submit",
    font=("Arial", 16),
    bg="lightblue",
    command=submit_name
)
submit_button.pack(pady=20, anchor="w", padx=10)

# Run the Tkinter event loop
root.mainloop()