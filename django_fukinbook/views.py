from decorators import facebook_auth_required
from django.contrib import auth
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from graph_api import ExampleAPI
from session import FacebookSession
from django.conf import settings
import utils
import logging

@csrf_exempt
@facebook_auth_required
def test(request):
    api = ExampleAPI(request.access_token)
    me = api.get_upcoming_birthdates()

    return HttpResponse('JSON: ' + str(me))

@csrf_exempt
@facebook_auth_required
def canvas(request):
    return HttpResponse('<a href="/test">Test</a>')

@csrf_exempt
def login(request):
    auth_url = utils.create_authorize_url(state=request.META.get('HTTP_REFERER'))
    next_url = request.GET.get('state') or settings.MAIN_URL
    error = None
    
    if request.GET:
        if 'code' in request.GET:
            logging.debug('CODE FOUND')
            session = FacebookSession(request.GET['code'])
            user = auth.authenticate(session=session)
            if user:
                if user.is_active:
                    logging.debug('ACTIVE USER')
                    auth.login(request, user)
                    return redirect(next_url)
                else:
                    logging.error('User is not active.')
                    error = 'AUTH_DISABLED'
            else:
                logging.error('User does not exists.')
                error = 'AUTH_FAILED'
        elif 'error_reason' in request.GET:
            logging.error('Facebook authentication failed.')
            error = 'AUTH_DENIED'
    elif request.user.is_authenticated():
        logging.debug('AUTHORIZED USER')
        return redirect(next_url)

    template_context = {'error': error, 'auth_url': auth_url}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


