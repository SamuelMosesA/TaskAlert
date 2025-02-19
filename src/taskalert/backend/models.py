from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from taskalert.backend.database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    tasks = relationship("Task", back_populates="section")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, index=True)
    description = Column(String, nullable=True)
    reminder_time = Column(DateTime, index=True)
    is_completed = Column(Boolean, default=False)
    section_id = Column(Integer, ForeignKey("sections.id"))

    section = relationship("Section", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task")

class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    step = Column(String)
    is_completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))

    task = relationship("Task", back_populates="subtasks")