# Create your models here.
from django.db import models
from django.contrib.auth.models import User
       
class Token(models.Model):

    access_token = models.CharField(max_length=300, unique=True)
    expires = models.IntegerField(null=False)
        
    user = models.ForeignKey(User, null=False)
    uid = models.BigIntegerField(unique=True, null=False)
        
    class Meta:
        unique_together = (('user', 'uid'), ('access_token', 'expires'))
