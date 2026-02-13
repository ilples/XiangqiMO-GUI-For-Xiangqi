import tkinter as tk
from gui import MainGUI

def main():
    """
    Main entry point for the Xiangqi analysis application.
    Creates the main window and starts the Tkinter event loop.
    """
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()