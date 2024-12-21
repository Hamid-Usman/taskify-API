from django.db.models.signals import post_save, post_delete

from .models import Cards, Columns
from django.dispatch import receiver

@receiver(post_delete, sender=Cards)
def handle_card_create(sender, instance, created, **kwargs):
    if created:
        print(f"Card Created {instance}")