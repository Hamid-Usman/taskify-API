from django.db.models.signals import post_save, post_delete

from .models import Cards, Columns
from django.dispatch import receiver