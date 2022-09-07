from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from .models import MyUser

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_related_handler(sender, instance, created, **kwargs):
    """
    Once a new User instance was saved:
    Check User instance, if this is new instance (created is True)
    then create a MyUser for this user.
    """
    if not created:
        return
    default_data = dict(balance=0)
    instance.MyUser = MyUser.objects.create(user=instance, **default_data)