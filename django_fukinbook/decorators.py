from models import Token
from settings import LOGGER as logger
from django.shortcuts import redirect
from django.http import Http404
import settings
import datetime
import time
from utils import create_authorize_url
from graph_api import GraphAPI

def facebook_auth_required(f):
    def wrap(request, *args, **kwargs):
        login_url = '/login/'     
        authorize_url = create_authorize_url()
        
        try:
            token = Token.objects.get(user=request.user)
        except Exception, e:
            logger.error(e)
            return redirect(login_url)
        
        timestamp_now = time.mktime(datetime.datetime.utcnow().timetuple())
        if token.expires < timestamp_now:
            return redirect(authorize_url)
        
        api = GraphAPI(token.access_token)
        me = api.get()
        if 'error' in me:
            error = me['error']
            if error['type'] == 'OAuthException':
                if 'code' in error:
                    code = error['code']
                    if code == 601:
                        raise Http404
                    elif code == 190:
                        pass
            return redirect(authorize_url)
        
        return f(request, token.access_token, me, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__ 
    return wrap
