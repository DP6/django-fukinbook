from models import Token
from settings import LOGGER as logger
from django.shortcuts import redirect
from django.http import Http404
import settings
import datetime
import time
from utils import create_authorize_url
from graph_api import GraphAPI
from session import FacebookSessionError

def facebook_auth_required(f):
    def wrap(request, *args, **kwargs):    
        authorize_url = create_authorize_url()
        
        try:
            token = Token.objects.get(user=request.user)
        except Exception, e:
            logger.error(e)
            return redirect(settings.FACEBOOK_LOGIN_URI)
        
        timestamp_now = time.mktime(datetime.datetime.utcnow().timetuple())
        if token.expires < timestamp_now:
            logger.warn('Token expired. Trying to fetch a new one.')
            return redirect(authorize_url)
        
        request.access_token = token.access_token
        try:
            return f(request, *args, **kwargs)
        except FacebookSessionError, e:
            logger.error(e)
            return redirect(authorize_url)        
        
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__ 
    return wrap
