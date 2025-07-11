# Muszaktervezo/models/user.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy import ForeignKey
import enum

class RoleEnum(enum.Enum):
    ADMIN = "Admin"
    USER = "Felhasználó"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # sima string MVP-re
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="users")

    shift_assignments = relationship(
        "ShiftAssignment",
        back_populates="user",
        foreign_keys="[ShiftAssignment.user_id]"
    )