import tkinter as tk
from tkinter import messagebox

# This list will act as our simple database to store student records
student_records = []

def add_student():
    """Adds a new student record to the list, validating that all fields are filled."""
    # Get values from the entry fields
    student_id = entry_id.get()
    name = entry_name.get()
    program = entry_program.get()
    block = entry_block.get()
    gsuite_account = entry_gsuite.get()

    # --- NEW VALIDATION LOGIC ---
    # Create a list of fields and their names for easy iteration and user feedback
    fields_to_check = [
        (student_id, "Student ID"),
        (name, "Name"),
        (program, "Program"),
        (block, "Block"),
        (gsuite_account, "Gsuite Account")
    ]
    
    # Check if any mandatory field is empty
    for value, field_name in fields_to_check:
        if not value:
            # If a field is empty, show an error message and stop the function
            messagebox.showerror("Error", f"Ang field na '{field_name}' ay kailangang lagyan ng laman.")
            return # Exit the function immediately if validation fails
    # --- END NEW VALIDATION LOGIC ---

    # Check if the student ID already exists (existing logic)
    for record in student_records:
        if record['Student ID'] == student_id:
            messagebox.showerror("Error", f"Student ID {student_id} already exists.")
            return

    # Create a dictionary for the new record (this part runs only if all validations pass)
    new_record = {
        'Student ID': student_id,
        'Name': name,
        'Program': program,
        'Block': block,
        'Gsuite Account': gsuite_account
    }
    student_records.append(new_record)
    messagebox.showinfo("Success", "Student record added successfully!")
    clear_entries() # Clear fields after adding

def view_records():
    """Displays all current student records in the text area."""
    text_area.config(state=tk.NORMAL) # Enable the text area for editing
    text_area.delete('1.0', tk.END) # Clear previous content
    
    if not student_records:
        text_area.insert(tk.END, "No student records found.")
    else:
        for record in student_records:
            for key, value in record.items():
                text_area.insert(tk.END, f"{key}: {value}\n")
            text_area.insert(tk.END, "------------------------\n") # Separator between records
            
    text_area.config(state=tk.DISABLED) # Disable editing by the user

def update_student():
    """Updates an existing student record based on the Student ID."""
    student_id = entry_id.get()
    
    # Simple check for ID field before update attempt
    if not student_id:
        messagebox.showerror("Error", "Student ID cannot be empty for update.")
        retur

    found = False
    for record in student_records:
        if record['Student ID'] == student_id:
            # Update the fields if new values are provided in the entry boxes
            if entry_name.get(): record['Name'] = entry_name.get()
            if entry_program.get(): record['Program'] = entry_program.get()
            if entry_block.get(): record['Block'] = entry_block.get()
            if entry_gsuite.get(): record['Gsuite Account'] = entry_gsuite.get()
            found = True
            break
            
    if found:
        messagebox.showinfo("Success", f"Student ID {student_id} updated successfully!")
        view_records() # Refresh the view
    else:
        messagebox.showerror("Error", f"Student ID {student_id} not found.")

def delete_student():
    """Deletes a student record based on the Student ID."""
    student_id = entry_id.get()

    # Simple check for ID field before delete attempt
    if not student_id:
        messagebox.showerror("Error", "Student ID cannot be empty for deletion.")
        return

    global student_records
    # Filter the list to keep only records that don't match the ID
    initial_count = len(student_records)
    student_records = [record for record in student_records if record['Student ID'] != student_id]
    
    if len(student_records) < initial_count:
        messagebox.showinfo("Success", f"Student ID {student_id} deleted successfully!")
        view_records() # Refresh the view
        clear_entries()
    else:
        messagebox.showerror("Error", f"Student ID {student_id} not found.")

def clear_entries():
    """Helper function to clear all input fields."""
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_program.delete(0, tk.END)
    entry_block.delete(0, tk.END)
    entry_gsuite.delete(0, tk.END)

# --- UI Setup ---

# Main Window configuration
root = tk.Tk()
root.title("Attendify: Mark Your Presence")
root.geometry("1000x700") # Set a default size
bg_color = "#D3D3D3" # Light gray background color
root.configure(bg=bg_color)

# Frame for entry fields and labels (left side)
entry_frame = tk.Frame(root, bg=bg_color, padx=10, pady=10)
entry_frame.grid(row=0, column=0, sticky="nw")

tk.Label(entry_frame, text="Enter Details:", font=("Helvetica", 12, "bold"), bg=bg_color).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

# Labels and Entry Widgets
tk.Label(entry_frame, text="Student ID:", bg=bg_color).grid(row=1, column=0, sticky="e")
entry_id = tk.Entry(entry_frame, width=30)
entry_id.grid(row=1, column=1, pady=5)

tk.Label(entry_frame, text="Name:", bg=bg_color).grid(row=2, column=0, sticky="e")
entry_name = tk.Entry(entry_frame, width=30)
entry_name.grid(row=2, column=1, pady=5)

tk.Label(entry_frame, text="Program:", bg=bg_color).grid(row=3, column=0, sticky="e")
entry_program = tk.Entry(entry_frame, width=30)
entry_program.grid(row=3, column=1, pady=5)

tk.Label(entry_frame, text="Block:", bg=bg_color).grid(row=4, column=0, sticky="e")
entry_block = tk.Entry(entry_frame, width=30)
entry_block.grid(row=4, column=1, pady=5)

tk.Label(entry_frame, text="Gsuite Account:", bg=bg_color).grid(row=5, column=0, sticky="e")
entry_gsuite = tk.Entry(entry_frame, width=30)
entry_gsuite.grid(row=5, column=1, pady=5)

# Frame for buttons (right side)
button_frame = tk.Frame(root, bg=bg_color, padx=10, pady=10)
button_frame.grid(row=0, column=1, sticky="w")

# Buttons for CRUD operations
tk.Button(button_frame, text="ADD", command=add_student, width=15).grid(row=0, column=0, pady=5, padx=5)
tk.Button(button_frame, text="UPDATE", command=update_student, width=15).grid(row=0, column=1, pady=5, padx=5)
tk.Button(button_frame, text="VIEW", command=view_records, width=15).grid(row=1, column=0, pady=5, padx=5)
tk.Button(button_frame, text="DELETE", command=delete_student, width=15).grid(row=1, column=1, pady=5, padx=5)

# Student Record Display Area
tk.Label(root, text="Student Record", font=("Helvetica", 12, "bold"), bg=bg_color).grid(row=1, column=0, columnspan=2, pady=(20, 5))

# Text widget to display records (set to disabled by default)
text_area = tk.Text(root, height=10, width=70, state=tk.DISABLED)
text_area.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Start the Tkinter event loop
root.mainloop()
