from decorators import facebook_auth_required
from django.contrib import auth
from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from graph_api import ExampleAPI, GraphAPI
from session import FacebookSession
from django.conf import settings
import utils
import logging
import simplejson


@csrf_exempt
@facebook_auth_required
def async_test(request):
    api = GraphAPI(request.access_token)
    task1 = {'id': 'significant_other',
             'fql': '''select name, uid from user where uid in 
             (select significant_other_id from user where uid=me())'''}

    task2 = {'id': 'family_birthdates',
             'fql': '''select name, birthday_date, relationship_status, 
             significant_other_id, family from user where uid = me()'''}

    tasks = [task1, task2]
    api.start_async_tasks(tasks)
    processed_tasks = api.tasks
    logging.debug(processed_tasks)

    return HttpResponse(simplejson.dumps(processed_tasks))


@csrf_exempt
@facebook_auth_required
def test(request):
    api = ExampleAPI(request.access_token)
    me = api.get_upcoming_birthdates()

    return HttpResponse(simplejson.dumps(me))


@csrf_exempt
@facebook_auth_required
def canvas(request):
    logging.debug(request.user)
    response = '''<a href="/test">Test</a><br />
    <a href="/test_async">Async Test</a><br />
    <a href="/logout">Logout</a>'''
    return HttpResponse(response)


@csrf_exempt
def login(request):
    next_url = request.GET.get('next')
    state_url = request.GET.get('state')
    if not next_url or next_url == 'None':
        if state_url:
            next_url = state_url
        else:
            next_url = settings.MAIN_URL

    error = None
    if request.GET:
        if 'code' in request.GET:
            logging.debug('CODE FOUND')
            facebook_session = FacebookSession(request.GET['code'])
            user = auth.authenticate(facebook_session=facebook_session,
                                     django_session=request.session,
                                     user=request.user or None)
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

    auth_url = utils.create_authorize_url(state=next_url)
    template_context = {'error': error, 'auth_url': auth_url}
    return render_to_response('login.html', template_context,
                              context_instance=Context(request))


@facebook_auth_required
def logout(request):
#    Uncomment these two lines if you want to revoke fb_token
#    on logout
#
#    graph_api = GraphAPI(request.access_token)
#    graph_api.revoke_token(request.access_token)

    auth.logout(request)
    return redirect(settings.MAIN_URL)

