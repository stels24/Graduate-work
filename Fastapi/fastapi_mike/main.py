from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import or_
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./fastapimike.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# User model
class User(Base):
    """
    Модель пользователя для хранения информации о пользователях.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tasks = relationship("Task", back_populates="user")


# Task model
class Task(Base):
    """
    Модель задачи для хранения информации о задачах.
    """
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String)
    data_created = Column(DateTime)
    data_end_plan = Column(DateTime)
    status = Column(String)
    data_end = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")

Base.metadata.create_all(bind=engine)


# Pydantic models for task form and filter form
class TaskForm(BaseModel):
    """
    Модель формы задачи для валидации данных задачи.
    """
    name: str
    description: str
    category: str
    data_end_plan: datetime
    status: str


class FilterForm(BaseModel):
    """
    Модель формы фильтра для валидации данных фильтра.
    """
    date: Optional[datetime]
    name: Optional[str]
    status: Optional[str]
    priority: Optional[str]

# Endpoints for login, registration, task addition, editing, deletion, and filtering
@app.get("/")
async def index(request: Request):
    """
    Маршрут для отображения главной страницы.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Маршрут для аутентификации пользователя.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user or not pwd_context.verify(password, user.hashed_password):
        return {"message": "Invalid username or password"}

    # Authenticate user and redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=303)
    request.session["user_id"] = user.id
    return response


@app.get("/register")
async def register(request: Request):
    """
    Маршрут для отображения страницы регистрации.
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    """
    Маршрут для регистрации пользователя.
    """
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        db.close()
        return {"message": "Username already exists"}

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    response = RedirectResponse(url="/login")
    return response #{"message": "Registration successful"}


@app.get("/add-task")
async def add_task_get(request: Request):
    """
    Маршрут для отображения страницы добавления задачи.
    """
    return templates.TemplateResponse("add_task.html", {"request": request})


@app.get("/edit-task/{task_id}")
async def edit_task(request: Request, task_id: int):
    """
    Маршрут для отображения страницы редактирования задачи.
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()

    if not task:
        return {"message": "Task not found"}

    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})


@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Маршрут для отображения панели управления.
    """
    if "user_id" not in request.session:
        return RedirectResponse(url="/login")

    user_id = request.session["user_id"]
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    tasks = db.query(Task).filter(Task.user_id == user_id).all()

    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.status == "completed"])
    in_progress_tasks = len([task for task in tasks if task.status == "in_progress"])
    planned_tasks = len([task for task in tasks if task.status == "planned"])
    statistics = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "planned_tasks": planned_tasks,
    }

    db.close()

    return templates.TemplateResponse("dashboard.html", {"request": request, "tasks": tasks, "statistics": statistics})


@app.get("/add-task")
async def add_task_get(request: Request):
    """
    Маршрут для отображения страницы добавления задачи.
    """
    # Render the add task page
    return templates.TemplateResponse("add_task.html", {"request": request})


@app.post("/add-task")
async def add_task_post(request: Request, task_data: TaskForm = Depends()):
    """
    Маршрут для добавления задачи в базу данных.
    """
    # Add the task to the database
    db = SessionLocal()
    new_task = Task(
        name=task_data.name,
        description=task_data.description,
        category=task_data.category,
        data_created=datetime.now(),
        data_end_plan=task_data.data_end_plan,
        status=task_data.status,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    # Redirect the user to the dashboard page
    return responses.RedirectResponse(url="/dashboard", status_code=303)


@app.post("/edit-task/{task_id}")
async def edit_task(request: Request, task_id: int, task_data: TaskForm = Depends()):
    """
    Маршрут для редактирования задачи в базе данных.
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return {"message": "Task not found"}

    task.name = task_data.name
    task.description = task_data.description
    task.category = task_data.category
    task.data_end_plan = task_data.data_end_plan
    task.status = task_data.status

    db.commit()
    db.refresh(task)
    db.close()

    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/delete-task/{task_id}")
async def delete_task(task_id: int):
    """
    Маршрут для удаления задачи из базы данных.
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return {"message": "Task not found"}

    db.delete(task)
    db.commit()
    db.close()

    return {"message": "Task deleted successfully"}


@app.post("/filter-tasks")
async def filter_tasks(filter_data: FilterForm = Depends()):
    """
    Маршрут для фильтрации задач в базе данных.
    """
    db = SessionLocal()
    query = db.query(Task)

    if filter_data.date:
        query = query.filter(Task.data_created == filter_data.date)

    if filter_data.name:
        query = query.filter(Task.name.ilike(f"%{filter_data.name}%"))

    if filter_data.status:
        query = query.filter(Task.status == filter_data.status)

    if filter_data.priority:
        query = query.filter(Task.priority == filter_data.priority)

    tasks = query.all()
    db.close()

    return {"tasks": tasks}


@app.get("/logout")
async def logout_get():
    """
    Маршрут для отображения страницы выхода из системы.
    """
    # Redirect the user to the login page
    response=RedirectResponse(url="/", status_code=303)
    return response


@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Маршрут для выхода из системы.
    """
    # Invalidate the user's session or token
    # ...
    # Redirect the user to the login page
    response=RedirectResponse(url="/", status_code=303)
    return response

from sqlalchemy.exc import IntegrityError


def create_test_user_and_tasks():
    """
    Функция для создания тестового пользователя и задач в базе данных.
    """
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == "testuser").first()

    if existing_user:
        print("Test user already exists")
    else:
        test_user = User(username="testuser", hashed_password=pwd_context.hash("1q2w3e"))
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        for i in range(10):
            task = Task(
                name=f"Task {i+1}",
                description=f"Description for task {i+1}",
                category="Test Category",
                data_created=datetime.now(),
                data_end_plan=datetime.now() + timedelta(days=7),
                status="Planned",
                user_id=test_user.id
            )
            db.add(task)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Error adding tasks to database")

    db.close()

#create_test_user_and_tasks()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

