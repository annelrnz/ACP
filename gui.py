from tkinter import *

window = Tk()

def click():
    print("Yes")

window.geometry("300x300")
window.title("444")

""" label = Label(window,
              text="I miss you",
              font=('Courier New',18,'bold'),
              fg='black',
              bg='pink',
              relief=RAISED,
              bd=20,
              padx=10,
              pady=5)
label.pack() """

button = Button(window,text='Will you marry me?')
button.config(command=click)
button.config(font=('Arial',16,'italic'))
button.config(bg='white')
button.pack()

window.mainloop()

