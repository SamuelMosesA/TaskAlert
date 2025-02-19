from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from taskalert.backend import crud, models, schemas
from taskalert.backend.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sections Endpoints
@app.post("/sections/", response_model=schemas.Section, tags=["sections"])
def create_section_api(section: schemas.SectionCreate, db: Session = Depends(get_db)):
    db_section = crud.get_section_by_name(db, name=section.name)
    if db_section:
        raise HTTPException(status_code=400, detail="Section name already registered")
    return crud.create_section(db=db, section=section)

@app.get("/sections/", response_model=List[schemas.Section], tags=["sections"])
def read_sections_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sections = crud.get_sections(db, skip=skip, limit=limit)
    return sections

@app.get("/sections/{section_id}", response_model=schemas.SectionWithTasks, tags=["sections"])
def read_section_api(section_id: int, db: Session = Depends(get_db)):
    db_section = crud.get_section(db, section_id=section_id)
    if db_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

@app.put("/sections/{section_id}", response_model=schemas.Section, tags=["sections"])
def update_section_api(section_id: int, section_update: schemas.SectionUpdate, db: Session = Depends(get_db)):
    db_section = crud.update_section(db, section_id=section_id, section_update=section_update)
    if db_section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

@app.delete("/sections/{section_id}", tags=["sections"])
def delete_section_api(section_id: int, db: Session = Depends(get_db)):
    if crud.delete_section(db, section_id=section_id):
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Section not found")

# Tasks Endpoints
@app.post("/tasks/", response_model=schemas.Task, tags=["tasks"])
def create_task_api(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@app.get("/tasks/", response_model=List[schemas.Task], tags=["tasks"])
def read_tasks_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.Task, tags=["tasks"])
def read_task_api(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task, tags=["tasks"])
def update_task_api(task_id: int, task_update: schemas.FullTaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task_full(db, task_id=task_id, task_update_full=task_update)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}", tags=["tasks"])
def delete_task_api(task_id: int, db: Session = Depends(get_db)):
    if crud.delete_task(db, task_id=task_id):
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/sections/{section_id}/tasks", response_model=List[schemas.Task], tags=["tasks"])
def read_tasks_by_section_api(section_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_section(db, section_id=section_id, skip=skip, limit=limit)
    return tasks

# Subtasks Endpoints
@app.post("/tasks/{task_id}/subtasks/", response_model=schemas.Subtask, tags=["subtasks"])
def create_subtask_api(task_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    return crud.create_subtask(db=db, subtask=subtask, task_id=task_id)

@app.get("/tasks/{task_id}/subtasks/", response_model=List[schemas.Subtask], tags=["subtasks"])
def read_subtasks_by_task_api(task_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subtasks = crud.get_subtasks_by_task(db, task_id=task_id, skip=skip, limit=limit)
    return subtasks

@app.put("/subtasks/{subtask_id}", response_model=schemas.Subtask, tags=["subtasks"])
def update_subtask_api(subtask_id: int, subtask_update: schemas.FullSubtaskUpdate, db: Session = Depends(get_db)):
    print(f"Received subtask_update for id {subtask_id}: {subtask_update}") # Added logging here
    db_subtask = crud.update_subtask_full(db, subtask_id=subtask_id, subtask_update_full=subtask_update)
    if db_subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return db_subtask

@app.delete("/subtasks/{subtask_id}", tags=["subtasks"])
def delete_subtask_api(subtask_id: int, db: Session = Depends(get_db)):
    if crud.delete_subtask(db, subtask_id=subtask_id):
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Subtask not found")