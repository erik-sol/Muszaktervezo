# Muszaktervezo/gui/views/shift_view.py
import tkinter as tk
from tkinter import Canvas
from datetime import date, timedelta
from database.connection import get_session
from models.user import User
from models.shift import ShiftAssignment, ShiftType
from gui.views.shift_editor import ShiftEditor
from models.department import Department

CELL_WIDTH = 120
CELL_HEIGHT = 40
DAYS = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

class ShiftCanvasView(tk.Frame):
    def __init__(self, master, logged_in_user):
        super().__init__(master)
        self.logged_in_user = logged_in_user
        self.session = get_session()
        self.start_date = self._get_monday(date.today())
        self.users = []
        self.shifts = []

        # Scrollozható canvas
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = Canvas(canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows és macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux fel (régi X11)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux le

        
        # Navigációs gombok a hétváltáshoz
        nav_frame = tk.Frame(self)
        nav_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Button(nav_frame, text="← Előző hét", command=self.prev_week).pack(side=tk.LEFT, padx=5, pady=2)
        tk.Button(nav_frame, text="Aktuális hét", command=self.reset_to_today).pack(side=tk.LEFT, padx=5, pady=2)
        tk.Button(nav_frame, text="Következő hét →", command=self.next_week).pack(side=tk.LEFT, padx=5, pady=2)

        # Hét dátumtartomány label
        self.week_label = tk.Label(nav_frame, text="")
        self.week_label.pack(side=tk.RIGHT, padx=10)

        self.draw()

    def _get_monday(self, d):
        return d - timedelta(days=d.weekday())

    def prev_week(self):
        self.start_date -= timedelta(days=7)
        self.draw()

    def next_week(self):
        self.start_date += timedelta(days=7)
        self.draw()

    def reset_to_today(self):
        self.start_date = self._get_monday(date.today())
        self.draw()

    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows & macOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw(self):
        try:
            if not self.winfo_exists():
                return

            self.canvas.delete("all")

            self.users = (
                self.session.query(User)
                .outerjoin(User.department)
                .order_by(Department.name.nullsfirst(), User.last_name)
                .all()
            )
            self.shifts = self.session.query(ShiftAssignment).all()

            week_end = self.start_date + timedelta(days=6)
            self.week_label.config(text=f"{self.start_date.strftime('%Y.%m.%d')} - {week_end.strftime('%Y.%m.%d')}")

            for col, day in enumerate(DAYS):
                x = (col + 1) * CELL_WIDTH
                current_date = self.start_date + timedelta(days=col)
                label = f"{day} ({current_date.strftime('%m.%d')})"
                self.canvas.create_rectangle(x, 0, x + CELL_WIDTH, CELL_HEIGHT, fill="#dddddd")
                self.canvas.create_text(x + CELL_WIDTH // 2, CELL_HEIGHT // 2, text=label)

            current_department = None
            row_offset = 1
            row = 0

            for user in self.users:
                if user.department != current_department:
                    current_department = user.department
                    y = (row + row_offset) * CELL_HEIGHT
                    self.canvas.create_rectangle(0, y, CELL_WIDTH * 8, y + CELL_HEIGHT, fill="#cccccc")
                    dept_name = current_department.name if current_department else "Ismeretlen"
                    self.canvas.create_text(10, y + CELL_HEIGHT // 2, anchor="w", text=dept_name)
                    row += 1

                y = (row + row_offset) * CELL_HEIGHT
                self.canvas.create_rectangle(0, y, CELL_WIDTH, y + CELL_HEIGHT, fill="#eeeeee")
                self.canvas.create_text(CELL_WIDTH // 2, y + CELL_HEIGHT // 2,
                                        text=f"{user.first_name} {user.last_name}", anchor="center")

                for col in range(7):
                    current_date = self.start_date + timedelta(days=col)
                    x = (col + 1) * CELL_WIDTH
                    user_shift = next((s for s in self.shifts if s.user_id == user.id and s.date == current_date), None)
                    color = "#ffffff"
                    text = ""

                    if user_shift:
                        shift_type = self.session.query(ShiftType).get(user_shift.shift_type_id)
                        color = shift_type.color if shift_type else "#cccccc"
                        text = shift_type.name if shift_type else "?"

                    self.canvas.create_rectangle(x, y, x + CELL_WIDTH, y + CELL_HEIGHT, fill=color, outline="black",
                                                tags=("cell", f"{user.id},{current_date}"))
                    self.canvas.create_text(x + 5, y + 5, anchor="nw", text=text, font=("Arial", 9))

                row += 1

            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        except tk.TclError:
            return

    def on_click(self, event):
        try:
            col = event.x // CELL_WIDTH - 1
            row = event.y // CELL_HEIGHT - 1
            if col < 0 or row < 0:
                return

            selected_date = self.start_date + timedelta(days=col)

            row_offset = 1
            current_row = 0
            current_department = None
            selected_user = None

            for user in self.users:
                if user.department != current_department:
                    current_department = user.department
                    current_row += 1
                if row == current_row:
                    selected_user = user
                    break
                current_row += 1

            if not selected_user:
                return

            is_admin = self.logged_in_user.role.value == "Admin"
            is_self = selected_user.id == self.logged_in_user.id
            is_editable_date = selected_date > date.today() + timedelta(days=3)

            if not is_admin and (not is_self or not is_editable_date):
                return

            existing = next((s for s in self.shifts if s.user_id == selected_user.id and s.date == selected_date), None)

            editor = ShiftEditor(self, existing_assignment=existing, default_user=selected_user, default_date=selected_date)
            self.wait_window(editor)
            self.draw()

        except tk.TclError:
            return
