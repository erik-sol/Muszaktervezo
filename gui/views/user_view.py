# Muszaktervezo/gui/views/user_view.py
import tkinter as tk
from tkinter import ttk, messagebox

from database.connection import get_session
from models.user import User
from models.department import Department  # Új import

from enum import Enum

class RoleEnum(Enum):
    ADMIN = "Admin"
    USER = "Felhasználó"

class UserView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Felhasználók kezelése")
        self.geometry("600x400")

        self.session = get_session()

        # Treeview + Scrollbar keret
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbar először!
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Teljes név", "Email", "Részleg"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        self.tree.heading("Teljes név", text="Teljes név")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Részleg", text="Részleg")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.tree.yview)

        # Gombok
        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(btn_frame, text="Új felhasználó", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Szerkesztés", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Törlés", command=self.delete_user).pack(side=tk.LEFT, padx=5)

        self.refresh()


    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for user in self.session.query(User).all():
            full_name = f"{user.first_name} {user.last_name}"
            dept = user.department.name if user.department else ""
            self.tree.insert("", "end", iid=user.id, values=(full_name, user.email, dept))

    def add_user(self):
        self.open_editor()

    def edit_user(self):
        selected = self.tree.selection()
        if selected:
            user_id = int(selected[0])
            user = self.session.get(User, user_id)
            self.open_editor(user)

    def delete_user(self):
        selected = self.tree.selection()
        if selected and messagebox.askyesno("Megerősítés", "Biztosan törölni szeretnéd a felhasználót?"):
            user_id = int(selected[0])
            user = self.session.get(User, user_id)
            self.session.delete(user)
            self.session.commit()
            self.refresh()

    def open_editor(self, user=None):
        from models.user import RoleEnum

        editor = tk.Toplevel(self)
        editor.title("Felhasználó szerkesztése" if user else "Új felhasználó")
        editor.geometry("350x500")

        tk.Label(editor, text="Vezetéknév:").pack()
        last_name_entry = tk.Entry(editor)
        last_name_entry.pack()

        tk.Label(editor, text="Keresztnév:").pack()
        first_name_entry = tk.Entry(editor)
        first_name_entry.pack()

        tk.Label(editor, text="Felhasználónév:").pack()
        username_entry = tk.Entry(editor)
        username_entry.pack()

        tk.Label(editor, text="Email:").pack()
        email_entry = tk.Entry(editor)
        email_entry.pack()

        tk.Label(editor, text="Részleg:").pack()
        departments = self.session.query(Department).order_by(Department.name).all()
        department_map = {d.name: d for d in departments}
        department_combo = ttk.Combobox(editor, values=list(department_map.keys()), state="readonly")
        department_combo.pack()

        tk.Label(editor, text="Jelszó:").pack()
        password_entry = tk.Entry(editor, show="*")
        password_entry.pack()
        tk.Label(editor, text="(Hagyd üresen, ha nem módosítod)", font=("Arial", 8)).pack(pady=(0, 5))

        tk.Label(editor, text="Jogosultság:").pack()
        role_combo = ttk.Combobox(editor, values=[role.name for role in RoleEnum])
        role_combo.pack()

        if user:
            first_name_entry.insert(0, user.first_name)
            last_name_entry.insert(0, user.last_name)
            username_entry.insert(0, user.username)
            email_entry.insert(0, user.email)
            if user.department:
                department_combo.set(user.department.name)
            role_combo.set(user.role.name if user.role else RoleEnum.USER.name)

        def save():
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            department_name = department_combo.get().strip()
            password = password_entry.get().strip()
            role_name = role_combo.get()

            if not all([first_name, last_name, username, email, department_name, role_name]):
                messagebox.showwarning("Hiba", "Minden mező kitöltése kötelező (jelszó kivétel szerkesztésnél).")
                return

            department = department_map.get(department_name)
            role = RoleEnum[role_name]

            if user:
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                user.department = department
                user.role = role
                if password:
                    user.password = password
            else:
                if not password:
                    messagebox.showwarning("Hiba", "Új felhasználónál a jelszó kötelező.")
                    return
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password,
                    department=department,
                    role=role
                )
                self.session.add(new_user)

            self.session.commit()
            editor.destroy()
            self.refresh()

        tk.Button(editor, text="Mentés", command=save).pack(pady=10)
