# Muszaktervezo/models/shift.py
from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class ShiftType(Base):
    __tablename__ = "shift_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)

    assignments = relationship("ShiftAssignment", back_populates="shift_type")

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    shift_type_id = Column(Integer, ForeignKey("shift_types.id"))
    date = Column(Date, nullable=False)
    note = Column(String)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="shift_assignments", foreign_keys=[user_id])
    shift_type = relationship("ShiftType", back_populates="assignments")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
