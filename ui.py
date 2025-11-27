import tkinter as tk
from tkinter import messagebox, ttk # Import ttk para sa treeview components ba

# Here mas-store info ng students na galing kay prof habang hindi pa connected sa database
student_records = []

def add_student():
    """Adds a new student record to the list, validating that all fields are filled."""
    # Pag-get ng values from entry fields
    student_id = entry_id.get()
    name = entry_name.get()
    program = entry_program.get()
    block = entry_block.get()
    gsuite_account = entry_gsuite.get()

    # Create a list of fields and their names for easy iteration and user feedback
    fields_to_check = [
        (student_id, "Student ID"),
        (name, "Name"),
        (program, "Program"),
        (block, "Block"),
        (gsuite_account, "Gsuite Account")
    ]
    
    # Dapat walang field ang blanko
    for value, field_name in fields_to_check:
        if not value:
           # Lalabas ito kapag may hindi nilagyan na field
            messagebox.showerror("Error!", f"'{field_name}' cannot be empty.")
            return

    # Checker lang to make sure na walang magkaparehas na STUDENT ID since parang primary key siya
    for record in student_records:
        if record['Student ID'] == student_id:
            messagebox.showerror("Error", f"Student ID {student_id} already exists.")
            return

    # Magr-run lang ito after makalampas sa validation
    new_record = {
        'Student ID': student_id,
        'Name': name,
        'Program': program,
        'Block': block,
        'Gsuite Account': gsuite_account
    }
    student_records.append(new_record)
    messagebox.showinfo("Success", "Student record added successfully!")
    clear_entries() # Clear all fields after adding
    view_records() # Refresh the Treeview display

def view_records():
    """Displays all current student records in the Treeview format."""
    # Clear existing records from the Treeview
    for record in tree_view.get_children():
        tree_view.delete(record)
    
    # Insert new data into the Treeview
    for record in student_records:
        tree_view.insert('', tk.END, values=(
            record['Student ID'], 
            record['Name'], 
            record['Program'], 
            record['Block'], 
            record['Gsuite Account']
        ))

def update_student():
    """Updates an existing student record based on the Student ID."""
    student_id = entry_id.get()
    if not student_id:
        messagebox.showerror("Error!", "Student ID cannot be empty for update.")
        return

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
    if not student_id:
        messagebox.showerror("Error", "Student ID cannot be empty for deletion.")
        return

    global student_records
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

# Para sa main window
root = tk.Tk()
root.title("Attendify: Mark Your Presence")
root.geometry("1000x700") # Fixed size ng window
bg_color = "pink" # Pink as background color
root.configure(bg=bg_color)
root.resizable(False, False)


root.grid_columnconfigure(0, weight=1) 
root.grid_columnconfigure(1, weight=1) 
root.grid_rowconfigure(2, weight=1)   

entry_frame = tk.Frame(root, bg=bg_color, padx=10, pady=10)
entry_frame.grid(row=0, column=0, sticky="nsew") 

tk.Label(entry_frame, text="Enter Student Details:", font=("Arial", 12, "bold"), bg=bg_color).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")


tk.Label(entry_frame, text="Student ID:", bg=bg_color).grid(row=1, column=0, sticky="w")
entry_id = tk.Entry(entry_frame, width=30)
entry_id.grid(row=1, column=1, pady=5, sticky="ew")

tk.Label(entry_frame, text="Name:", bg=bg_color).grid(row=2, column=0, sticky="w")
entry_name = tk.Entry(entry_frame, width=30)
entry_name.grid(row=2, column=1, pady=5, sticky="ew")

tk.Label(entry_frame, text="Program:", bg=bg_color).grid(row=3, column=0, sticky="w")
entry_program = tk.Entry(entry_frame, width=30)
entry_program.grid(row=3, column=1, pady=5, sticky="ew")

tk.Label(entry_frame, text="Block:", bg=bg_color).grid(row=4, column=0, sticky="w")
entry_block = tk.Entry(entry_frame, width=30)
entry_block.grid(row=4, column=1, pady=5, sticky="ew")

tk.Label(entry_frame, text="Gsuite Account:", bg=bg_color).grid(row=5, column=0, sticky="w")
entry_gsuite = tk.Entry(entry_frame, width=30)
entry_gsuite.grid(row=5, column=1, pady=5, sticky="ew")

entry_frame.grid_columnconfigure(1, weight=1)

button_frame = tk.Frame(root, bg=bg_color, padx=10, pady=10)
button_frame.grid(row=0, column=1, sticky="we") 

# For buttons, included na ang sizes, position and even appearance nila
tk.Button(button_frame, text="ADD", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=add_student).grid(row=0, column=0, pady=5, padx=5, sticky="ew")
tk.Button(button_frame, text="UPDATE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=update_student).grid(row=0, column=1, pady=5, padx=5, sticky="ew")
tk.Button(button_frame, text="VIEW", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=view_records).grid(row=1, column=0, pady=5, padx=5, sticky="ew")
tk.Button(button_frame, text="DELETE", font=("Arial", 10, "bold"), fg="black", bg="silver", width=10, command=delete_student).grid(row=1, column=1, pady=5, padx=5, sticky="ew")

button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

tk.Label(root, text="Student Record", font=("Arial", 20, "bold"), bg=bg_color).grid(row=1, column=0, columnspan=2, pady=(20, 5))


# Define columns 
columns = ('student_id', 'name', 'program', 'block', 'gsuite_account')

tree_view = ttk.Treeview(root, columns=columns, show='headings')
# sticky="nsew" makes the tree view expand in all directions within its cell
tree_view.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Configure column headings and widths
tree_view.heading('student_id', text='Student ID')
tree_view.heading('name', text='Name')
tree_view.heading('program', text='Program')
tree_view.heading('block', text='Block')
tree_view.heading('gsuite_account', text='Gsuite Account')

# To adjust the sizes ng mga columns
tree_view.column('student_id', anchor=tk.CENTER, width=100)
tree_view.column('name', anchor=tk.W, width=150)
tree_view.column('program', anchor=tk.W, width=100)
tree_view.column('block', anchor=tk.CENTER, width=80)
tree_view.column('gsuite_account', anchor=tk.W, width=150)

# Add a scrollbar to the Treeview para kapag maraming records puwede tingnan hanggang baba
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree_view.yview)
tree_view.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=2, column=2, sticky='ns') 

# Start the tkinter event loop
root.mainloop()
