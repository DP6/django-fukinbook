from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, HttpResponse
from django.template import Context
from django.views.decorators.csrf import csrf_exempt

import pprint

import settings
from models import Token
from session import FacebookSession
from graph_api import GraphAPI

def canvas(request):
    try:
        token = Token.objects.get(user=request.user)
    except:
        HttpResponseRedirect('/404/')
    api = GraphAPI(token.access_token)
    a = api.get_upcoming_birthdates()
    pp = pprint.PrettyPrinter()
    pp.pprint(a)
    return HttpResponse(a['data'])

@csrf_exempt
def login(request):
    error = None

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

    template_context = {'settings': settings, 'error': error}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


