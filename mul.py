import tkinter as tk
from tkinter import messagebox

# This is our "student notebook" - a list to hold our students (each has ID, name, program, block, and GSuite)
students = []

# Function to add a new student (CREATE)
def add_student():
    student_id = id_entry.get()
    name = name_entry.get()
    program = program_entry.get()
    block = block_entry.get()
    gsuite = gsuite_entry.get()
    if student_id and name and program and block and gsuite:
        students.append({
            "id": student_id,
            "name": name,
            "program": program,
            "block": block,
            "gsuite": gsuite
        })
        update_list()
        clear_entries()
    else:
        messagebox.showerror("Oops!", "You need to fill in all the boxes!")

# Function to clear the entry boxes
def clear_entries():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    program_entry.delete(0, tk.END)
    block_entry.delete(0, tk.END)
    gsuite_entry.delete(0, tk.END)

# Function to show all students (READ)
def update_list():
    student_list.delete(0, tk.END)
    for student in students:
        student_list.insert(tk.END, f"ID: {student['id']} - {student['name']} ({student['program']}, Block {student['block']}, {student['gsuite']})")

# Function to change a student (UPDATE)
def update_student():
    selected = student_list.curselection()
    if selected:
        index = selected[0]
        student_id = id_entry.get()
        name = name_entry.get()
        program = program_entry.get()
        block = block_entry.get()
        gsuite = gsuite_entry.get()
        if student_id and name and program and block and gsuite:
            students[index] = {
                "id": student_id,
                "name": name,
                "program": program,
                "block": block,
                "gsuite": gsuite
            }
            update_list()
            clear_entries()
        else:
            messagebox.showerror("Oops!", "You need to fill in all the boxes!")
    else:
        messagebox.showerror("Oops!", "Pick a student from the list first!")

# Function to remove a student (DELETE)
def delete_student():
    selected = student_list.curselection()
    if selected:
        index = selected[0]
        del students[index]
        update_list()
    else:
        messagebox.showerror("Oops!", "Pick a student from the list first!")

# Make the main window (like the cover of the notebook)
root = tk.Tk()
root.title("My Student Notebook")
root.geometry("600x400")

# Frame for the entry fields (to keep them neat)
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)

# Labels and entry boxes side by side (like "Student ID:" then the box right next to it)

tk.Label(entry_frame, text="Student ID:").grid(row=0, column=0, sticky="e", padx=5)
id_entry = tk.Entry(entry_frame)
id_entry.grid(row=0, column=1, padx=5)

tk.Label(entry_frame, text="Name:").grid(row=1, column=0, sticky="e", padx=5)
name_entry = tk.Entry(entry_frame)
name_entry.grid(row=1, column=1, padx=5)

tk.Label(entry_frame, text="Program:").grid(row=2, column=0, sticky="e", padx=5)
program_entry = tk.Entry(entry_frame)
program_entry.grid(row=2, column=1, padx=5)

tk.Label(entry_frame, text="Block:").grid(row=3, column=0, sticky="e", padx=5)
block_entry = tk.Entry(entry_frame)
block_entry.grid(row=3, column=1, padx=5)

tk.Label(entry_frame, text="GSuite Account:").grid(row=4, column=0, sticky="e", padx=5)
gsuite_entry = tk.Entry(entry_frame)
gsuite_entry.grid(row=4, column=1, padx=5)

# Buttons for actions (like buttons on a toy)
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Student", command=add_student).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Update Student", command=update_student).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Delete Student", command=delete_student).pack(side=tk.LEFT, padx=5)

# List box to show students (like pages in the notebook)
student_list = tk.Listbox(root)
student_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Start the program
update_list()  # Show any students at the start (none at first)
root.mainloop()
