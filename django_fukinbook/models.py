from django.db import models
from django.contrib.auth.models import User
import datetime
import time
from session import FacebookSession
from django.http import HttpResponseRedirect
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    pic_small = models.URLField()
    pic = models.URLField()
    pic_big = models.URLField()
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User, dispatch_uid="users-profilecreation-signal")
       
class Token(models.Model):

    access_token = models.CharField(max_length=254, unique=True)
    _expires = models.IntegerField(null=False)
        
    user = models.ForeignKey(User, null=False)
    uid = models.BigIntegerField(unique=True, null=False)
        
    def set_expires(self, value):
        timestamp_now = time.mktime(datetime.datetime.utcnow().timetuple())
        self._expires = (timestamp_now + int(value))

    def get_expires(self):
        return self._expires
    
    expires = property(get_expires, set_expires)
    
    class Meta:
        unique_together = (('user', 'uid'), ('access_token', '_expires'))