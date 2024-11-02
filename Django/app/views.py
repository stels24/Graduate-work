from app.models import Task, Category
from app.forms import TaskForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import views as auth_views

def add_task(request):
    """
    Представление для добавления новой задачи.
    """
    categories = Category.objects.all()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form, 'categories': categories})


def edit_task(request, task_id):
    """
    Представление для редактирования существующей задачи.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})


def delete_task(request, task_id):
    """
    Представление для удаления существующей задачи.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('dashboard')


def login_view(request):
    """
    Представление для аутентификации пользователя.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')


def dashboard(request):
    """
    Представление для отображения панели управления пользователя.
    """
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'tasks': tasks, 'user': request.user})


def delete_task(request, task_id):
    """
    Представление для удаления существующей задачи.
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'delete_task.html', {'task': task})


def index(request):
    """
    Представление для отображения главной страницы.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def register(request):
    """
    Представление для регистрации нового пользователя.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
