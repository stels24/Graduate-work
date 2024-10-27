import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangomike.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.contrib.auth.models import User
# остальной код скрипта

from app.models import Task, Category
from datetime import datetime, timedelta


application = get_wsgi_application()

# Создайте или получите пользователя
user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpassword'})

# Создайте категории
categories = []
for i in range(1, 6):
    category = Category.objects.create(name=f'Категория задачи {i}')
    categories.append(category)

# Создайте задачи
for i in range(1, 21):
    category = categories[i % len(categories)]
    data_created = datetime.now() - timedelta(days=i)
    data_end_plan = data_created + timedelta(days=1)
    Task.objects.create(
        name=f'Задача {i}',
        description=f'Описание задачи  {i} подробное',
        category=category,
        data_created=data_created,
        data_end_plan=data_end_plan,
        status='planned',
        user=user
    )
