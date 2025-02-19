from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from taskalert.backend import models, schemas

# Section CRUD
def get_section(db: Session, section_id: int):
    return db.query(models.Section).filter(models.Section.id == section_id).first()

def get_section_by_name(db: Session, name: str):
    return db.query(models.Section).filter(models.Section.name == name).first()

def get_sections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Section).offset(skip).limit(limit).all()

def create_section(db: Session, section: schemas.SectionCreate):
    db_section = models.Section(name=section.name)
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def update_section(db: Session, section_id: int, section_update: schemas.SectionUpdate):
    db_section = get_section(db, section_id=section_id)
    if db_section:
        for key, value in section_update.model_dump(exclude_unset=True).items():
            setattr(db_section, key, value)
        db.commit()
        db.refresh(db_section)
    return db_section

def delete_section(db: Session, section_id: int):
    db_section = get_section(db, section_id=section_id)
    if db_section:
        db.delete(db_section)
        db.commit()
        return True
    return False

# Task CRUD
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task_full(db: Session, task_id: int, task_update_full: schemas.FullTaskUpdate):
    db_task = get_task(db, task_id=task_id)
    if db_task:
        for key, value in task_update_full.model_dump(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id=task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def get_tasks_by_section(db: Session, section_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.section_id == section_id).offset(skip).limit(limit).all()

# Subtask CRUD
def create_subtask(db: Session, subtask: schemas.SubtaskCreate, task_id: int):
    db_subtask = models.Subtask(**subtask.model_dump(), task_id=task_id)
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask

def get_subtasks_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Subtask).filter(models.Subtask.task_id == task_id).offset(skip).limit(limit).all()

def get_subtask(db: Session, subtask_id: int):
    return db.query(models.Subtask).filter(models.Subtask.id == subtask_id).first()

def update_subtask_full(db: Session, subtask_id: int, subtask_update_full: schemas.SubtaskCompletionUpdate): # Use SubtaskUpdate schema
    db_subtask = get_subtask(db, subtask_id=subtask_id)
    if db_subtask:
        for key, value in subtask_update_full.model_dump(exclude_unset=True).items():
            setattr(db_subtask, key, value)
        db.commit()
        db.refresh(db_subtask)
    return db_subtask

def delete_subtask(db: Session, subtask_id: int):
    db_subtask = get_subtask(db, subtask_id=subtask_id)
    if db_subtask:
        db.delete(db_subtask)
        db.commit()
        return True
    return False