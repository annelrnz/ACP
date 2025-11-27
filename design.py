import tkinter as tk
from tkinter import messagebox

#FUNCTIONS

students = []

def add_info():
    student_id = id.get()
    name = name.get()
    program = program.get()
    block = block.get()
    gsuite = gsuite.get()
    if student_id and name and program and block and gsuite:
        students.append({
            "ID": student_id,
            "Name": name,
            "Program": program,
            "Block": block,
            "Gsuite Account": gsuite
        })
        update_list()
        clear_entries()
    else:
        messagebox.showerror("Oops!", "You need to fill in all the boxes!")

def clear_entries():
    id.delete(0, tk.END)
    name.delete(0, tk.END)
    program.delete(0, tk.END)
    block.delete(0, tk.END)
    gsuite.delete(0, tk.END)

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
        student_id = id.get()
        name = name.get()
        program = program.get()
        block = block.get()
        gsuite = gsuite.get()
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






#MAIN WINDOW
window = tk.Tk()
window.title("Attendify: Mark Your Presence")
window.geometry("1500x700") 

window.resizable(False, False) 
window.configure(bg="#d9d9d9")  

details= tk.Label(
    window,
    text="Enter Details:",
    font=("Arial", 15, "bold"),
    fg="black",
)
details.pack(pady=7, anchor="w", padx=10)

id = tk.Label(
    window,
    text="Student ID:",
    font=("Arial", 10),
    fg="black",
    bg="white"
)
id.pack(pady=7, anchor="w", padx=10)
id= tk.Entry(
    window,
    font=("Arial", 10),
    width=18
)
id.pack(pady=0, padx=8, anchor="w")



               
name = tk.Label(
    window,
    text="Name:",
    font=("Arial", 10),
    fg="black",
    bg="white"
)
name.pack(pady=7, anchor="w", padx=10)
name = tk.Entry(
    window,
    font=("Arial", 10),
    width=18
)
name.pack(pady=0, padx=8, anchor="w")

program = tk.Label(
    window,
    text="Program:",
    font=("Arial", 10),
    fg="black",
    bg="white"
)
program.pack(pady=7, anchor="w", padx=10)
program= tk.Entry(
    window,
    font=("Arial", 10),
    width=18
)
program.pack(pady=0, padx=8, anchor="w")

block = tk.Label(
    window,
    text="Block:",
    font=("Arial", 10),
    fg="black",
    bg="white"
)
block.pack(pady=7, anchor="w", padx=10)
block = tk.Entry(
    window,
    font=("Arial", 10),
    width=18
)
block.pack(pady=0, padx=8, anchor="w")

gsuite = tk.Label(
    window,
    text="Gsuite Account:",
    font=("Arial", 10),
    fg="black",
    bg="white"
)
gsuite.pack(pady=7, anchor="w", padx=10)
gsuite = tk.Entry(
    window,
    font=("Arial", 10),
    width=18
)
gsuite.pack(pady=0, padx=8, anchor="w")

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Student", command=add_info).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Update Student", command=update_student).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Delete Student", command=delete_student).pack(side=tk.LEFT, padx=5)

# List box to show students (like pages in the notebook)
student_list = tk.Listbox(window)
student_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Start the program
update_list()  # Show any students at the start (none at firs


window.mainloop()