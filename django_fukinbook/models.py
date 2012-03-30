# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import datetime
import time
from session import FacebookSession
from django.http import HttpResponseRedirect
       
class Token(models.Model):

    access_token = models.CharField(max_length=300, unique=True)
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