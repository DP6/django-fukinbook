from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from graph_api import GraphAPI
from models import Token
from session import FacebookSession
import logging
import settings
import urllib

def canvas(request):
    try:
        token = Token.objects.get(user=request.user)
    except:
        HttpResponseRedirect('/404/')
    api = GraphAPI(token.access_token)
    a = api.get_significant_other()

    return HttpResponse(a)

def create_authorize_url():
    AUTH_URI = 'oauth/authorize'
    
    params = {
      'client_id': settings.FACEBOOK_APP_ID,
      'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
      'scope': settings.FACEBOOK_APP_SCOPE}
    authorize_url = '%s%s?%s' % (settings.GRAPH_API_URL, AUTH_URI, 
                                 urllib.urlencode(params))
    return authorize_url

@csrf_exempt
def login(request):
    error = None
    
    if 'refresh_token' in request.GET:
        redirect(create_authorize_url())
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/canvas/')

    if request.GET:
        if 'code' in request.GET:
            session = FacebookSession(request.GET['code'])
            user = auth.authenticate(session=session)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/canvas/')
                else:
                    error = 'AUTH_DISABLED'
            else:
                error = 'AUTH_FAILED'
        elif 'error_reason' in request.GET:
            error = 'AUTH_DENIED'

    template_context = {'error': error, 'auth_url': create_authorize_url()}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


