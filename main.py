import tkinter as tk
from calendar_app import CalendarApp

def main():
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()