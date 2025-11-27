import tkinter as tk

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
    bg="#efdecd"  # match window background
)
title_label.pack(pady=20)  # Add space at the top

# ---- Student Name Label ----
name_label = tk.Label(
    root,
    text="Student Name:",
    font=("Times New Roman", 16),
    fg="black",
    bg="#efdecd"
)
name_label.pack(pady=10, anchor="w", padx=10)  # left-aligned with some padding

# ---- Text Box (Entry) ----
name_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=20
)
name_entry.pack(pady=5, padx=10, anchor="w")  # align with label

# Run the Tkinter event loop
root.mainloop()