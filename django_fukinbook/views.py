from django.contrib import auth
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from graph_api import GraphAPI, ExampleAPI
from models import Token
from session import FacebookSession
from settings import LOGGER as logger
import settings
import urllib

def canvas(request):
    try:
        token = Token.objects.get(user=request.user)
    except Exception, e:
        logger.error(e)
        raise Http404
    api = ExampleAPI(token.access_token)
    a = api.get()
    #logger.debug(type(a))
    if isinstance(a, HttpResponseRedirect):
        return a

    return HttpResponse('JSON: ' + str(a))

def create_authorize_url():
    AUTH_URI = 'oauth/authorize'
    
    params = {
      'client_id': settings.FACEBOOK_APP_ID,
      'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
      'scope': settings.FACEBOOK_APP_SCOPE,
      'popup': 'false'}
    authorize_url = '%s%s?%s' % (settings.GRAPH_API_URL, AUTH_URI, 
                                 urllib.urlencode(params))
    return authorize_url

@csrf_exempt
def login(request):
    next_url = '/canvas/'
    error = None
    
    if request.GET:
        if 'refresh_token' in request.GET:
            logger.debug('MUST REFRESH TOKEN')
            return redirect(create_authorize_url())
        if 'code' in request.GET:
            logger.debug('CODE FOUND')
            session = FacebookSession(request.GET['code'])
            user = auth.authenticate(session=session)
            if user:
                if user.is_active:
                    logger.debug('ACTIVE USER')
                    auth.login(request, user)
                    return redirect(next_url)
                else:
                    error = 'AUTH_DISABLED'
            else:
                error = 'AUTH_FAILED'
        elif 'error_reason' in request.GET:
            error = 'AUTH_DENIED'
    elif request.user.is_authenticated():
        logger.debug('AUTHORIZED USER')
        return redirect(next_url)

    template_context = {'error': error, 'auth_url': create_authorize_url()}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


