from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, HttpResponse
from django.template import Context
from django.views.decorators.csrf import csrf_exempt

import urlparse
import urllib

import settings
import models

def yay(request):
    return HttpResponse('yay!')

class FacebookResponse():
    URL = 'https://graph.facebook.com/oauth/access_token?'
    args = {
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
        self.args['code'] = self.code
        return '%s%s' % (self.URL, urllib.urlencode(self.args))
    
    def _get_response(self):
        url = self._encode_url()
        response = urlparse.parse_qs(urllib.urlopen(url).read())
        self.access_token = response['access_token'][0]
        self.expires = response['expires'][0]
    
@csrf_exempt
def login(request):
    error = None

    if request.user.is_authenticated():
        return HttpResponseRedirect('/yay/')

    if request.GET:
        if 'code' in request.GET:
            response = FacebookResponse(request.GET['code'])
            access_token = response.access_token
            expires = response.expires

            facebook_session = models.FacebookSession.objects.get_or_create(
                access_token=access_token,
            )[0]
            facebook_session.expires = expires
            facebook_session.save()

            user = auth.authenticate(token=access_token)
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


