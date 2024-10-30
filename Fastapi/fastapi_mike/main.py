import logging
from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from fastapi import FastAPI, Form, Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./fastapimike.db"
# connect_args={"check_same_thread": False} - настройка необходима при работе с базой данных sqlite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# User model
class User(Base):
    """Класс описания пользователя

    Args:
        Base (_type_): Базовое представление модели таблицы БД с классом
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tasks = relationship("Task", back_populates="user")


# Task model
class Task(Base):
    """Класс описания модели задачки

    Args:
        Base (_type_): Базовое представление модели таблицы БД с классом
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
    """Класс для описания формы задачки для валидации Pydantic'ом

    Args:
        BaseModel (_type_): Базовая модель разбора и валидации данных с формы ввода данных
    """
    name: str
    description: str
    category: str
    data_end_plan: datetime
    status: str


class FilterForm(BaseModel):
    """Класс для описания формы фильтрации для валидации Pydantic'ом

    Args:
        BaseModel (_type_): Базовая модель разбора и валидации данных с формы ввода данных
    """
    date: Optional[datetime]
    name: Optional[str]
    status: Optional[str]
    priority: Optional[str]


# Endpoints for login, registration, task addition, editing, deletion, and filtering
@app.get("/")
async def index(request: Request):
    """Загрузка главной страницы при запуске приложения

    Args:
        request (Запрос): Простой запрос

    Returns:
        Форма стартового экрана : Возвращает сам запрос с шаблоном загруженной стартовой страницы
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Метод авторизации

    Args:
        request (Request): Запрос
        username (str, optional): Имя пользователя. Defaults to Form(...).
        password (str, optional): Пароль. Defaults to Form(...).

    Returns:
        Форма ответа перехода: Шаблон личного кабинета после авторизации либо сообщение, что не совпадает имя пользователя или пароль
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
    """Метод получения шаблона страницы регистрации

    Args:
        request (Request): Запрос

    Returns:
        _type_: Возвращает построенный шаблон на страницу вызова
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    """Метод создания записи в БД с регистрацией пользователя

    Args:
        username (str, optional): Логин пользователя. Defaults to Form(...).
        password (str, optional): Пароль в незашифрованном виде, который будет зашифрован на этапе поступления в БД. Defaults to Form(...).

    Returns:
        Перенаправление: Перенаправление на страницу логина
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
    return response


@app.get("/add-task")
async def add_task_get(request: Request):
    """Метод получения формы создания заявки

    Args:
        request (Request): Запрос

    Returns:
        Шаблон: Шаблон формы создания заявки вида html-страницы
    """ 
    return templates.TemplateResponse("add_task.html", {"request": request})


@app.get("/edit-task/{task_id}")
async def edit_task(request: Request, task_id: int):
    """Получение формы редактирования задачки

    Args:
        request (Request): Запрос
        task_id (int): ИД задачки

    Returns:
        Сообщение: Сообщение об отсутствии задачки, если её нет либо форма редактирования задачи
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()

    if not task:
        return {"message": "Task not found"}

    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})


@app.get("/dashboard")
async def dashboard(request: Request):
    """Метод получения таблицы со списком задач (дашборд)

    Args:
        request (Request): Запрос

    Returns:
        Щаблон с дашбордом: Шаблон страницы с доской задач (дашбордом)
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


@app.post("/add_task")
async def add_task_post(request: Request, task_data: TaskForm = Depends()):
    """Метод добавления задачки БД после её создания

    Args:
        request (Request): Запрос
        task_data (TaskForm, optional): Форма со страницы со всеми необходимыми параметрами для создания новой записи в БД. Defaults to Depends().

    Returns:
        Ответ: Сообщение об успешном добавлении задачки в БД и на даш-борд
    """
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

    response = RedirectResponse(url="/dashboard", status_code=303)
    return response  #{"message": "Task added successfully"}


@app.post("/edit-task/{task_id}")
async def edit_task(request: Request, task_id: int, task_data: TaskForm = Depends()):
    """Сохранение изменения параметров задачки

    Args:
        request (Request): Запрос
        task_id (int): Идентификатор задачки в БД для её обновления
        task_data (TaskForm, optional): Данные с формы. Defaults to Depends().

    Returns:
        Перенаправление: Перенаправление на страницу со списком задач
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
    """Подтверждение удаления задачки

    Args:
        task_id (int): ИД задачки

    Returns:
        Сообщение: Сообщение об успешном удалении задачи в БД или сообщение, что такая задачка не найдена
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
    """Отправка запроса фильтрации списка задач

    Args:
        filter_data (FilterForm, optional): Данные с формы для применения фильтра. Defaults to Depends().

    Returns:
        Ответ: Список задач соответствующих правилам фильтра
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
