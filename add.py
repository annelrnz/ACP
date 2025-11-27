import tkinter as tk
from tkinter import messagebox

# This is our "toy box" - a list to hold our toys (each toy has a name and color)
toys = []

# Function to add a new toy (CREATE)
def add_toy():
    name = name_entry.get()
    color = color_entry.get()
    if name and color:
        toys.append({"name": name, "color": color})
        update_list()
        name_entry.delete(0, tk.END)
        color_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Oops!", "You need to fill in both name and color!")

# Function to show all toys (READ)
def update_list():
    toy_list.delete(0, tk.END)
    for toy in toys:
        toy_list.insert(tk.END, f"{toy['name']} - {toy['color']}")

# Function to change a toy (UPDATE)
def update_toy():
    selected = toy_list.curselection()
    if selected:
        index = selected[0]
        name = name_entry.get()
        color = color_entry.get()
        if name and color:
            toys[index] = {"name": name, "color": color}
            update_list()
            name_entry.delete(0, tk.END)
            color_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Oops!", "You need to fill in both name and color!")
    else:
        messagebox.showerror("Oops!", "Pick a toy from the list first!")

# Function to throw away a toy (DELETE)
def delete_toy():
    selected = toy_list.curselection()
    if selected:
        index = selected[0]
        del toys[index]
        update_list()
    else:
        messagebox.showerror("Oops!", "Pick a toy from the list first!")

# Make the main window (like the outside of the toy box)
root = tk.Tk()
root.title("My Toy Box")
root.geometry("400x300")

# Labels and entry boxes for name and color (like labels on drawers)
tk.Label(root, text="Toy Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Toy Color:").pack()
color_entry = tk.Entry(root)
color_entry.pack()

# Buttons for actions (like buttons on a toy)
button_frame = tk.Frame(root)
button_frame.pack()

tk.Button(button_frame, text="Add Toy", command=add_toy).pack(side=tk.LEFT)
tk.Button(button_frame, text="Update Toy", command=update_toy).pack(side=tk.LEFT)
tk.Button(button_frame, text="Delete Toy", command=delete_toy).pack(side=tk.LEFT)

# List box to show toys (like a window to see inside the box)
toy_list = tk.Listbox(root)
toy_list.pack(fill=tk.BOTH, expand=True)

# Start the program
update_list()  # Show any toys at the start (none at first)
root.mainloop()
