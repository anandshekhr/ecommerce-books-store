from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# Signal to automatically create and save the user profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create the profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)
    else:
        try:
            # Update the profile if it exists
            instance.profile.save()
        except UserProfile.DoesNotExist:
            # Create the profile if it doesn't exist (fallback)
            UserProfile.objects.create(user=instance)

