# Muszaktervezo/gui/views/shift_editor.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkcalendar import DateEntry
from sqlalchemy.orm import object_session

from database.connection import get_session
from models.user import User
from models.shift import ShiftType, ShiftAssignment

class ShiftEditor(tk.Toplevel):
    def __init__(self, master, existing_assignment=None, default_user=None, default_date=None, logged_in_user=None):
        super().__init__(master)
        self.title("Műszak szerkesztése" if existing_assignment else "Műszak hozzáadása")
        self.geometry("400x300")
        self.session = get_session() if not existing_assignment else None
        self.existing_assignment = existing_assignment
        self.logged_in_user = logged_in_user

        # Felhasználó kiválasztó
        tk.Label(self, text="Dolgozó:").pack()
        self.user_combo = ttk.Combobox(self)
        self.user_combo.pack()

        query = (self.session or object_session(existing_assignment)).query(User)
        if logged_in_user and logged_in_user.role.name == "USER":
            users = [logged_in_user]
        else:
            users = query.all()
            
        self.user_map = {f"{u.first_name} {u.last_name} ({u.email})": u.id for u in users}
        self.user_combo["values"] = list(self.user_map.keys())

        # Dátum naptár mező
        tk.Label(self, text="Dátum:").pack()
        self.date_entry = DateEntry(self, width=18, background='darkblue', foreground='white',
                                    borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack()

        # Műszak kiválasztó
        tk.Label(self, text="Műszak típusa:").pack()
        self.shift_combo = ttk.Combobox(self)
        self.shift_combo.pack()

        shifts = (self.session or object_session(existing_assignment)).query(ShiftType).all()
        self.shift_map = {s.name: s.id for s in shifts}
        self.shift_combo["values"] = list(self.shift_map.keys())

        # Alapértelmezett értékek betöltése
        if existing_assignment:
            user = (self.session or object_session(existing_assignment)).get(User, existing_assignment.user_id)
            shift = (self.session or object_session(existing_assignment)).get(ShiftType, existing_assignment.shift_type_id)
            self.user_combo.set(f"{user.first_name} {user.last_name} ({user.email})")
            self.date_entry.set_date(existing_assignment.date)
            self.shift_combo.set(shift.name if shift else "")
        else:
            if default_user:
                self.user_combo.set(f"{default_user.first_name} {default_user.last_name} ({default_user.email})")
            if default_date:
                self.date_entry.set_date(default_date)

        # Mentés gomb
        save_btn = tk.Button(self, text="Mentés", command=self.save_shift)
        save_btn.pack(pady=5)

        if existing_assignment:
            del_btn = tk.Button(self, text="Törlés", command=self.delete_shift, fg="red")
            del_btn.pack(pady=5)

    def save_shift(self):
        user_name = self.user_combo.get()
        selected_date = self.date_entry.get_date()
        shift_name = self.shift_combo.get()

        if user_name and selected_date and shift_name:
            session = self.session or object_session(self.existing_assignment)

            if self.existing_assignment:
                self.existing_assignment.user_id = self.user_map[user_name]
                self.existing_assignment.date = selected_date
                self.existing_assignment.shift_type_id = self.shift_map[shift_name]
            else:
                new_assignment = ShiftAssignment(
                    user_id=self.user_map[user_name],
                    date=selected_date,
                    shift_type_id=self.shift_map[shift_name],
                )
                session.add(new_assignment)

            session.commit()
            self.destroy()

    def delete_shift(self):
        if messagebox.askyesno("Megerősítés", "Biztosan törölni szeretnéd ezt a beosztást?"):
            session = object_session(self.existing_assignment)
            session.delete(self.existing_assignment)
            session.commit()
            self.destroy()
