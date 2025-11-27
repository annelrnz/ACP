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
root.geometry("500x400")

# Labels and entry boxes for student info (like labels on notebook pages)
tk.Label(root, text="Student ID:").pack()
id_entry = tk.Entry(root)
id_entry.pack()

tk.Label(root, text="Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Program:").pack()
program_entry = tk.Entry(root)
program_entry.pack()

tk.Label(root, text="Block:").pack()
block_entry = tk.Entry(root)
block_entry.pack()

tk.Label(root, text="GSuite Account:").pack()
gsuite_entry = tk.Entry(root)
gsuite_entry.pack()

# Buttons for actions (like buttons on a toy)
button_frame = tk.Frame(root)
button_frame.pack()

tk.Button(button_frame, text="Add Student", command=add_student).pack(side=tk.LEFT)
tk.Button(button_frame, text="Update Student", command=update_student).pack(side=tk.LEFT)
tk.Button(button_frame, text="Delete Student", command=delete_student).pack(side=tk.LEFT)

# List box to show students (like pages in the notebook)
student_list = tk.Listbox(root)
student_list.pack(fill=tk.BOTH, expand=True)

# Start the program
update_list()  # Show any students at the start (none at first)
root.mainloop()
