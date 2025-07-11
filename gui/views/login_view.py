# Muszaktervezo/gui/views/login_view.py
import tkinter as tk
from tkinter import messagebox

from database.connection import get_session
from models.user import User

import sys

class LoginView(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Bejelentkezés")
        self.geometry("300x220")
        self.on_success = on_success
        self.session = get_session()

        tk.Label(self, text="Felhasználónév:").pack(pady=(20, 5))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Jelszó:").pack(pady=(10, 5))
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        login_btn = tk.Button(self, text="Belépés", command=self.try_login)
        login_btn.pack(pady=15)

        self.bind("<Return>", self.try_login)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

    def try_login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.session.query(User).filter_by(username=username, password=password).first()
        if user:
            self.on_success(user)
            self.destroy()
        else:
            messagebox.showerror("Hibás belépés", "Helytelen felhasználónév vagy jelszó.")

    def quit_app(self):
        try:
            self.destroy()
        except tk.TclError:
            pass
        sys.exit(0)  # Ezzel leáll az egész alkalmazás
