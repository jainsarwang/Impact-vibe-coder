from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import models, database

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the ToDo API"}

@app.post("/todos/", response_model=models.Todo)
async def create_todo(todo: models.TodoCreate, db: Session = Depends(database.get_db)):
    db_todo = models.Todo(**todo.dict(), id=None) # Let the DB handle ID generation
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[models.Todo])
async def read_todos(skip: int = 0, limit: int = 100, completed: Optional[bool] = None, db: Session = Depends(database.get_db)):
    todos = db.query(models.Todo)
    if completed is not None:
        todos = todos.filter(models.Todo.completed == completed)
    todos = todos.offset(skip).limit(limit).all()
    return todos

@app.get("/todos/{todo_id}", response_model=models.Todo)
async def read_todo(todo_id: int, db: Session = Depends(database.get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.patch("/todos/{todo_id}", response_model=models.Todo)
async def update_todo(todo_id: int, todo: models.TodoUpdate, db: Session = Depends(database.get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=models.Todo)
async def delete_todo(todo_id: int, db: Session = Depends(database.get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return db_todo


# Additional filtering endpoint
@app.get("/todos/filter/", response_model=List[models.Todo])
async def filter_todos(
    priority: Optional[str] = None,
    due_date: Optional[date] = None,
    db: Session = Depends(database.get_db),
):
    query = db.query(models.Todo)

    if priority:
        query = query.filter(models.Todo.priority == priority)
    if due_date:
        query = query.filter(models.Todo.due_date == due_date)

    todos = query.all()
    return todos
