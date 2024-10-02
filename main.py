import tkinter as tk
from app import App

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application terminated.")
        app.tcp_client.stop()