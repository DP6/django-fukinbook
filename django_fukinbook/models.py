from django.db import models
from django.contrib.auth.models import User
import datetime
import time
from session import FacebookSession
from django.http import HttpResponseRedirect
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_app_user = models.BooleanField(default=False)
    uid = models.BigIntegerField(null=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User,
                  dispatch_uid="users-profilecreation-signal")
