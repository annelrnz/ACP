import tkinter as tk
from tkinter import messagebox

# Storage ng mga info ng students
student_records = []

def add_record():
    # Function para sa ADD and to get values from entry widgets
    student_id = entry_id.get()
    name = entry_name.get()
    program = entry_program.get()
    block = entry_block.get()
    gsuite = entry_gsuite.get()

    # To validate entries galing sa prof
    if student_id and name and program and block and gsuite:
        record = {
            "ID": student_id,
            "Name": name,
            "Program": program,
            "Block": block,
            "GSuite Acc": gsuite
        }
        student_records.append(record)
        update_listbox()
        clear_entries()
        messagebox.showinfo("ADD", "Student record added successfully!.")
    else:
        messagebox.showwarning("Error!", "Please fill in all fields.")

def update_listbox():
    """Function used to view all records and update the Listbox widget."""
    listbox_records.delete(0, tk.END) # Clear existing entries
    for index, record in enumerate(student_records):
        # Format the record for display in the listbox
        display_text = f"{index+1}. ID: {record['ID']} Name: {record['Name']}, Program: {record['Program']}, Block: {record['Block']}"
        listbox_records.insert(tk.END, display_text)

def clear_entries(event=None):
    """Clear the input fields."""
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_program.delete(0, tk.END)
    entry_block.delete(0, tk.END)
    entry_gsuite.delete(0, tk.END)

def select_record(event):
    """Load selected record data into entry fields for potential update/delete."""
    try:
        # Get the index of the selected item
        selected_index = listbox_records.curselection()[0]
        selected_record = student_records[selected_index]
        
        clear_entries() # Clear fields first
        entry_id.insert(tk.END, selected_record['ID'])
        entry_name.insert(tk.END, selected_record['Name'])
        entry_program.insert(tk.END, selected_record['Program'])
        entry_block.insert(tk.END, selected_record['Block'])
        entry_gsuite.insert(tk.END, selected_record['GSuite Acc'])
    except IndexError:
        pass # Handle case where no item is selected

def update_selected_record():
    """Update an existing student record."""
    try:
        selected_index = listbox_records.curselection()[0]
        # Update the record in the list with new data from entry fields
        student_records[selected_index]['ID'] = entry_id.get()
        student_records[selected_index]['Name'] = entry_name.get()
        student_records[selected_index]['Program'] = entry_program.get()
        student_records[selected_index]['Block'] = entry_block.get()
        student_records[selected_index]['GSuite Acc'] = entry_gsuite.get()
        update_listbox()
        clear_entries()
        messagebox.showinfo("Success", "Student record updated successfully.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a record to update.")

def delete_record():
    """Delete a selected student record."""
    try:
        selected_index = listbox_records.curselection()[0]
        del student_records[selected_index]
        update_listbox()
        clear_entries()
        messagebox.showinfo("Success", "Student record deleted successfully.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a record to delete.")

# --- Main GUI Setup ---

root = tk.Tk()
root.title("Attendify: Mark Your Presence")
root.geometry("1000x700")

# --- Input Frame ---
input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.grid(row=1, column=0, columnspan=3, sticky="ew")


tk.Label(input_frame, text="Enter Details:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

# Labels and Entry fields
fields = ["Student ID:", "Name:", "Program:", "Block:", "Gsuite Account:"]
entries = []
for i, field in enumerate(fields):
    tk.Label(input_frame, text=field).grid(row=i+1, column=0, sticky="e", pady=5, padx=5)
    entry = tk.Entry(input_frame, width=40)
    entry.grid(row=i+1, column=1, pady=5, padx=5)
    entries.append(entry)

# Assign entry widgets to specific variables for access in functions
entry_id, entry_name, entry_program, entry_block, entry_gsuite = entries

# --- Button Frame (CRUD Operations) ---
button_frame = tk.Frame(root, padx=10, pady=10)
button_frame.grid(row=1, column=3, rowspan=5, sticky="w")

# Buttons using grid layout for structure
tk.Button(button_frame, text="ADD", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=add_record).grid(row=0, column=0, pady=5)
tk.Button(button_frame, text="VIEW", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=update_listbox).grid(row=1, column=0, pady=5)
tk.Button(button_frame, text="UPDATE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=update_selected_record).grid(row=0, column=1, pady=5, padx=5)
tk.Button(button_frame, text="DELETE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=15, command=delete_record).grid(row=1, column=1, pady=5, padx=5)

# --- Display Frame ---
display_frame = tk.Frame(root, padx=10, pady=10)
display_frame.grid(row=6, column=0, columnspan=4, sticky="nsew")
root.grid_rowconfigure(6, weight=1) # Make display area expandable
root.grid_columnconfigure(0, weight=1)  

tk.Label(display_frame, text="Student Record", font=("Arial", 14, "bold")).pack(pady=(0, 10))

# Create a scrollbar for the listbox
scrollbar = tk.Scrollbar(display_frame)
listbox_records = tk.Listbox(display_frame, yscrollcommand=scrollbar.set, height=10)
scrollbar.config(command=listbox_records.yview)

# Arrange listbox and scrollbar
listbox_records.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Bind selection event to the select_record function
listbox_records.bind('<<ListboxSelect>>', select_record)

# Initial load of data (currently empty)
update_listbox()

# Start the Tkinter event loop
root.mainloop()

