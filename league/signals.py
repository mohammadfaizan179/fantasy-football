from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from league.models import Transaction


# Signal to prevent deletion
@receiver(pre_delete, sender=Transaction)
def prevent_inactive_transaction_deletion(sender, instance, **kwargs):
    if instance.inactive:
        raise ValidationError("Inactive transfers cannot be deleted.")
