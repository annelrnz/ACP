import tkinter as tk
from tkinter import messagebox, simpledialog

# List to store student names
student_list = []

# Function for the button action
def submit_name():
    student_name = name_entry.get().strip()

    if student_name:  # avoid saving empty input
        student_list.append(student_name)
        print("Student List:", student_list)

        # Update label display
        list_label.config(text="Saved Names: " + ", ".join(student_list))

        name_entry.delete(0, tk.END)  # clear textbox after submitting


# Function to delete a name
def delete_name():
    name_to_delete = name_entry.get().strip()

    if name_to_delete in student_list:
        student_list.remove(name_to_delete)
        print("Updated List:", student_list)

        # Update label
        list_label.config(text="Saved Names: " + ", ".join(student_list))

        name_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Not Found", f"'{name_to_delete}' is not in the list.")


# Function to update a name
def update_name():
    old_name = name_entry.get().strip()

    if old_name in student_list:
        # Ask user for the new name
        new_name = simpledialog.askstring("Update Name", f"Enter new name for '{old_name}':")

        if new_name:
            index = student_list.index(old_name)
            student_list[index] = new_name.strip()

            print("Updated List:", student_list)

            # Update the label
            list_label.config(text="Saved Names: " + ", ".join(student_list)) # tkinter widgets

            name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Invalid Input", "New name cannot be empty.") # tkinter messagebox module
    else:
        messagebox.showwarning("Not Found", f"'{old_name}' is not in the list.")


# Create the main window
root = tk.Tk()

# Set title and size
root.title("CICS Management System")
root.geometry("1500x600")  # width x height

# Make the window not resizable
root.resizable(False, False)

# Change the background color
root.configure(bg="#efdecd")  # light beige color

# ---- Title Label ----
title_label = tk.Label(
    root,
    text="Student Information Management System",
    font=("Arial", 24, "bold"),
    fg="darkblue",
    bg="#efdecd"
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

# ---- Submit Button ----
submit_button = tk.Button(
    root,
    text="Submit",
    font=("Arial", 16),
    bg="lightblue",
    command=submit_name
)
submit_button.pack(pady=10, anchor="w", padx=10)

# ---- Delete Button ----
delete_button = tk.Button(
    root,
    text="Delete",
    font=("Arial", 16),
    bg="red",
    fg="white",
    command=delete_name
)
delete_button.pack(pady=10, anchor="w", padx=10)

# ---- Update Button ----
update_button = tk.Button(
    root,
    text="Update",
    font=("Arial", 16),
    bg="orange",
    fg="black",
    command=update_name
)
update_button.pack(pady=10, anchor="w", padx=10)

# ---- Label Showing Saved Names ----
list_label = tk.Label(
    root,
    text="Saved Names: ",
    font=("Arial", 14),
    bg="#efdecd",
    fg="black",
    anchor="w"
)
list_label.pack(pady=10, anchor="w", padx=10)

# Run the Tkinter event loop
root.mainloop()