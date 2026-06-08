import customtkinter as ctk
from ui.main_window import MainWindow
from database.database import init_db

def main():
    # Initialize database
    init_db()

    # Set theme
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Start Application
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
