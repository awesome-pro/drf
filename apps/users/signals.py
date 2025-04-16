from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Import your User model - adjust the import if needed
from apps.users.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to handle user creation events.
    This can be used to create related models or perform actions when a user is created.
    """
    if created:
        # You can add any post-user creation logic here
        # For example, creating a profile, sending welcome emails, etc.
        pass
