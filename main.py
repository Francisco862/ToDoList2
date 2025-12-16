# main.py
import tkinter as tk
from ui.app import TodoApp

def main():
    root = tk.Tk()
    root.withdraw()  # zapobiega mrugnięciu okna podczas setupu

    root.update_idletasks()
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.state('zoomed')  # maksymalizacja dla Windows
    root.deiconify()      # po konfiguracji pokazujemy okno

    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
