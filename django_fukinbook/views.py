from decorators import facebook_auth_required
from django.contrib import auth
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from graph_api import GraphAPI, ExampleAPI
from models import Token
from session import FacebookSession
from settings import LOGGER as logger
from utils import create_authorize_url
import settings
import urllib

@facebook_auth_required
def canvas(request):
    api = ExampleAPI(request.access_token)
    me = api.get_upcoming_birthdates()

    return HttpResponse('JSON: ' + str(me))

@csrf_exempt
def login(request):
    auth_url = create_authorize_url()
    error = None
    
    if request.GET:
        if 'code' in request.GET:
            logger.debug('CODE FOUND')
            session = FacebookSession(request.GET['code'])
            user = auth.authenticate(session=session)
            if user:
                if user.is_active:
                    logger.debug('ACTIVE USER')
                    auth.login(request, user)
                    return redirect(settings.MAIN_URL)
                else:
                    error = 'AUTH_DISABLED'
            else:
                error = 'AUTH_FAILED'
        elif 'error_reason' in request.GET:
            error = 'AUTH_DENIED'
    elif request.user.is_authenticated():
        logger.debug('AUTHORIZED USER')
        return redirect(settings.MAIN_URL)

    template_context = {'error': error, 'auth_url': auth_url}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


