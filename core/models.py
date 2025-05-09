from django.db import models
from datetime import date
from users.models import User


class Boards(models.Model):
    title = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")

    def __str__(self):
        return self.title

class Columns(models.Model):
    title = models.CharField(max_length=15)
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name="columns")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

# Create your models here.
class Cards(models.Model):
    STATUS_CHOICES = [
        ('To-do', 'To-do'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Prioritize', 'Prioritize')
    ]
    task = models.CharField(max_length=30)
    position = models.PositiveIntegerField(default=0)
    description = models.TextField(default="", blank=True)
    due_date = models.DateField(default=date.today)
    column = models.ForeignKey(Columns, on_delete=models.CASCADE, related_name="cards")
    priority = models.CharField(max_length=40, choices=STATUS_CHOICES, default="To-do")
   # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    def __str__(self):
        return self.task