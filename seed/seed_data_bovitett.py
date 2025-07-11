# Muszaktervezo/seed/seed_data.py
from database.connection import get_session
from models.user import User, RoleEnum
from models.shift import ShiftType, ShiftAssignment
from models.department import Department
import datetime

def seed():
    from faker import Faker
    from random import choice, randint
    fake = Faker("hu_HU")

    session = get_session()

    # Részlegek
    department_names = ["Iroda", "Gyártás", "Raktár", "Lakatos üzem", "Forgácsoló", "Műanyag", "Minőségbiztosítás"]
    department_map = {}
    for name in department_names:
        dept = Department(name=name)
        session.add(dept)
        department_map[name] = dept
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

    today = datetime.date.today()

    # Felhasználók
    users = [
        User(first_name="Rendszer", last_name="Admin", username="admin", password="admin",
             email="admin@ceg.hu", role=RoleEnum.ADMIN, department=department_map["Iroda"])
    ]
    for _ in range(30):
        first = fake.first_name()
        last = fake.last_name()
        uname = f"{last.lower()}.{first.lower()}".replace(" ", "")
        email = f"{uname}@ceg.hu"
        department = choice(list(department_map.values()))
        user = User(first_name=first, last_name=last, username=uname, email=email,
                    password="1234", role=RoleEnum.USER, department=department)
        users.append(user)

    session.add_all(users)
    session.commit()

    # Műszakbeosztások
    all_users = session.query(User).all()
    assignments = []
    for user in all_users:
        for i in range(7):
            shift_type = shifts[randint(0, 1)]  # Csak a két normál műszak
            assignments.append(ShiftAssignment(
                user_id=user.id,
                shift_type_id=shift_type.id,
                date=today + datetime.timedelta(days=i)
            ))

    session.add_all(assignments)
    session.commit()
    session.close()
    print("✅ Nagy mennyiségű tesztadat betöltve!")


if __name__ == "__main__":
    seed()
    print("✅ Kezdő adatok betöltve!")
