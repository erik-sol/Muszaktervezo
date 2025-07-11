# Muszaktervezo/seed/seed_data.py
from database.connection import get_session
from models.user import User, RoleEnum
from models.shift import ShiftType, ShiftAssignment
from models.department import Department
import datetime

def seed():
    session = get_session()

    # Részlegek
    departments = ["Iroda", "Gyártás", "Raktár"]
    department_map = {}
    for name in departments:
        existing = session.query(Department).filter_by(name=name).first()
        if not existing:
            dept = Department(name=name)
            session.add(dept)
            session.flush()  # ID-t generál
            department_map[name] = dept
        else:
            department_map[name] = existing

    session.commit()

    # Műszaktípusok
    shifts = [
        ShiftType(name="6:00-14:00", color="#7ec8e3", start_time=datetime.time(6, 0), end_time=datetime.time(14, 0)),
        ShiftType(name="14:00-22:00", color="#ffb347", start_time=datetime.time(14, 0), end_time=datetime.time(22, 0)),
        ShiftType(name="Szabadság", color="#90ee90"),
        ShiftType(name="Home Office", color="#d3bce3"),
    ]
    session.add_all(shifts)
    session.commit()

    # Felhasználók
    users = [
        User(first_name="Rendszer", last_name="Admin", username="admin", password="admin", email="admin@ceg.hu", role=RoleEnum.ADMIN, department=department_map["Iroda"]),
        User(first_name="Kovács", last_name="Anna", username="kovacs.anna", password="1234", email="kovacs.anna@ceg.hu", department=department_map["Gyártás"]),
        User(first_name="Szabó", last_name="Béla", username="szabo.bela", password="1234", email="szabo.bela@ceg.hu", department=department_map["Raktár"]),
    ]
    session.add_all(users)
    session.commit()

    # Demo beosztások
    today = datetime.date.today()
    assignments = [
        ShiftAssignment(user_id=2, shift_type_id=1, date=today),
        ShiftAssignment(user_id=3, shift_type_id=2, date=today),
    ]
    session.add_all(assignments)
    session.commit()
    session.close()


if __name__ == "__main__":
    seed()
    print("✅ Kezdő adatok betöltve!")
