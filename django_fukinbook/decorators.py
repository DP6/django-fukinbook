from django.http import HttpResponseServerError
from django.shortcuts import redirect
from exceptions import FacebookGenericError, FacebookSessionError
from django.conf import settings
from utils import create_authorize_url
from django.core import urlresolvers
import datetime
import time
import logging


def facebook_auth_required(func):
    def wrap(request, *args, **kwargs):
        refresh_token_url = create_authorize_url(state=request.path)
        timeout = 60

        fb_token = request.session.get('fb_token')
        if not fb_token:
            logging.info(u'Facebook token not found. Will redirect to login')
            login_url = '/login?next={0}'.format(request.path)
            return redirect(login_url)

        timestamp_now = time.mktime(datetime.datetime.utcnow().timetuple())
        if fb_token['expires'] < timestamp_now + timeout:
            logging.warn('Token expired. Trying to fetch a new one.')
            return redirect(refresh_token_url)

        request.access_token = fb_token['access_token']
        try:
            return func(request, *args, **kwargs)
        except FacebookSessionError, e:
            logging.error(str(e))
            return redirect(refresh_token_url)
        except FacebookGenericError, e:
            logging.error(str(e))
            return HttpResponseServerError

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
