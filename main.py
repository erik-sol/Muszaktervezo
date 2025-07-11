# Muszaktervezo/main.py
import os
import pathlib
import tkinter as tk

from database.create_db import Base, engine
from seed.seed_data import seed
from gui.views.login_view import LoginView
from gui.main_window import MainWindow

current_user = None

def initialize_database():
    db_file = pathlib.Path("muszaktervezo.db")
    if not db_file.exists():
        print("⚡ Adatbázis nem található, létrehozás...")
        Base.metadata.create_all(bind=engine)
        seed()
    else:
        print("✅ Adatbázis már létezik, ugrunk a GUI-re")

def start_app(user):
    global current_user
    current_user = user
    root = MainWindow(logged_in_user=user)
    root.mainloop()

if __name__ == "__main__":
    #initialize_database()
    root = tk.Tk()
    
    root.withdraw()
    login = LoginView(root, on_success=start_app)
    login.mainloop()
