from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, HttpResponse
from django.template import Context
from django.views.decorators.csrf import csrf_exempt

import urlparse
import urllib
import simplejson

import settings
import models

def yay(request):
    return HttpResponse('yay!')


class FacebookSessionError(Exception):   
    def __init__(self, error_type, message):
        self.message = message
        self.type = error_type
        
    def get_message(self): 
        return self.message
    
    def get_type(self):
        return self.type
    
    def __unicode__(self):
        return u'%s: "%s"' % (self.type, self.message)


class FacebookSession:
    API_URL = 'https://graph.facebook.com/'
    TOKEN_URL = '%s%s' % (API_URL, 'oauth/access_token?')
    ARGS = {
        'client_id': settings.FACEBOOK_APP_ID,
        'client_secret': settings.FACEBOOK_APP_SECRET,
        'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
    }
    
    def __init__(self, code):
        self.code = code
        self.access_token = None
        self.expires = None
        self._get_response()        
        
    def _encode_url(self):
        self.ARGS['code'] = self.code
        return '%s%s' % (self.TOKEN_URL, urllib.urlencode(self.ARGS))
    
    def _get_response(self):
        url = self._encode_url()
        response = urlparse.parse_qs(urllib.urlopen(url).read())
        self.access_token = response['access_token'][0]
        self.expires = response['expires'][0]
        
    def get_user_profile(self, object_id='me', connection_type=None, metadata=False):
        url = '%s%s' % (self.API_URL, object_id)
        if connection_type:
            url += '/%s' % (connection_type)
        
        params = {'access_token': self.access_token}
        if metadata:
            params['metadata'] = 1
         
        url += '?%s' % urllib.urlencode(params)
        response = simplejson.load(urllib.urlopen(url))
        if 'error' in response:
            error = response['error']
            raise FacebookSessionError(error['type'], error['message'])
        return response
    
@csrf_exempt
def login(request):
    error = None

    if request.user.is_authenticated():
        return HttpResponseRedirect('/yay/')

    if request.GET:
        if 'code' in request.GET:
            session = FacebookSession(request.GET['code'])

            user = auth.authenticate(session=session)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/yay/')
                else:
                    error = 'AUTH_DISABLED'
            else:
                error = 'AUTH_FAILED'
        elif 'error_reason' in request.GET:
            error = 'AUTH_DENIED'

    template_context = {'settings': settings, 'error': error}
    return render_to_response('login.html', template_context, context_instance=Context(request))


