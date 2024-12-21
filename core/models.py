from django.db import models
from datetime import date


class Boards(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

class Columns(models.Model):
    title = models.CharField(max_length=15)
    board = models.ForeignKey(Boards, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

# Create your models here.
class Cards(models.Model):
    task = models.CharField(max_length=30)
    position = models.PositiveIntegerField(default=0)
    description = models.TextField(default="", blank=True)
    due_date = models.DateField(default=date.today)
    column = models.ForeignKey(Columns, on_delete=models.CASCADE)

    def __str__(self):
        return self.task