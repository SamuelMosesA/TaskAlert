from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class SubtaskBase(BaseModel):
    step: str
    is_completed: Optional[bool] = False

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskCompletionUpdate(BaseModel): 
    is_completed: Optional[bool] = None  # Make is_completed Optional for updates

class FullSubtaskUpdate(SubtaskBase):
    pass

class Subtask(SubtaskBase):
    id: int
    task_id: int

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    summary: str
    description: Optional[str] = None
    reminder_time: datetime
    is_completed: Optional[bool] = False

class TaskCreate(TaskBase):
    section_id: int

class TaskCompletionUpdate(BaseModel):
    is_completed: Optional[bool] = None  # Make is_completed Optional for updates

class FullTaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    section_id: int
    subtasks: List[Subtask] = []

    class Config:
        orm_mode = True

class SectionBase(BaseModel):
    name: str

class SectionCreate(SectionBase):
    pass

class SectionUpdate(SectionBase):
    pass

class Section(SectionBase):
    id: int
    tasks: List[Task] = []

    class Config:
        orm_mode = True

class SectionWithTasks(Section):
    tasks: List[Task]