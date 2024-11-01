from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Модель категории задач.
    """
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'app'

    def __str__(self):
        return self.name

class Task(models.Model):
    """
    Модель задачи.
    """
    STATUS_CHOICES = (
        ('planned', 'Запланирована'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    data_created = models.DateTimeField(auto_now_add=True)
    data_end_plan = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    data_end = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
