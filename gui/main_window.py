# Muszaktervezo/gui/main_window.py
import tkinter as tk
from gui.views.shift_view import ShiftCanvasView
from gui.views.shift_editor import ShiftEditor
from gui.views.user_view import UserView
from models.user import RoleEnum

class MainWindow(tk.Tk):
    def __init__(self, logged_in_user):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.title("Műszaktervező")
        self.geometry("1000x600")

        # Vezérlőgombsor
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(control_frame, text="+ Műszak hozzáadása", command=self.open_shift_editor).pack(side=tk.LEFT, padx=10, pady=5)

        # Felhasználók kezelése csak adminnak
        if self.logged_in_user.role == RoleEnum.ADMIN:
            tk.Button(control_frame, text="Felhasználók kezelése", command=self.open_user_view).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(control_frame, text="↻ Frissítés", command=self.refresh_view).pack(side=tk.LEFT, padx=10, pady=5)

        # Műszak nézet
        self.view = ShiftCanvasView(self, self.logged_in_user)
        self.view.pack(fill=tk.BOTH, expand=True)

    def open_shift_editor(self):
        editor = ShiftEditor(self, logged_in_user=self.logged_in_user)
        self.wait_window(editor)
        self.view.draw()

    def open_user_view(self):
        UserView(self)

    def refresh_view(self):
        self.view.draw()
