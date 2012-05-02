from django.http import HttpResponseServerError
from django.shortcuts import redirect
from exceptions import FacebookGenericError, FacebookSessionError
from models import Token
from django.conf import settings
from utils import create_authorize_url
from django.core import urlresolvers
import datetime
import time
import logging

def facebook_auth_required(func):
    def wrap(request, *args, **kwargs):    
        authorize_url = create_authorize_url()
        timeout = 60
        
        try:
            token = Token.objects.get(user=request.user)
        except Exception, e:
            logging.error(e)
            return redirect(urlresolvers.reverse('login'))
        
        timestamp_now = time.mktime(datetime.datetime.utcnow().timetuple())
        if token.expires < timestamp_now + timeout:
            logging.warn('Token expired. Trying to fetch a new one.')
            return redirect(authorize_url)
        
        request.access_token = token.access_token
        try:
            return func(request, *args, **kwargs)
        except FacebookSessionError, e:
            logging.error(e)
            return redirect(authorize_url)
        except FacebookGenericError, e:
            logging.error(e)
            return HttpResponseServerError(str(e))
        
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__ 
    return wrap
