from django.http import HttpResponseServerError
from exceptions import FacebookGenericError, FacebookSessionError
from django.conf import settings
import logging
import simplejson
import urllib
import datetime
from tornado import httpclient, ioloop, gen

class GraphAPI:
    ''' We are supposing that every request will have a session '''
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.async_queue = set()
        self.async_http_client = httpclient.AsyncHTTPClient()
        self.tasks = {}

    def start_async_tasks(self, tasks):
        self.tasks = tasks
        for key, task in tasks.items():
            self.async_get(task)

        ioloop.IOLoop.instance().start()

    @gen.engine
    def async_get(self, task, connection_type=None, metadata=False,
                  format='json'):
        fql = task.get('fql')
        path = task.get('path')
        self.async_queue.add(fql)
        logging.debug(task)
        token_url = self._create_token_url(path, fql, connection_type,
                                           metadata, format)

        response = yield gen.Task(self.async_http_client.fetch, token_url)
        if response.error:
            logging.error(response.error)
        else:
            task['response'] = response.body

        self.async_queue.remove(fql)
        if not self.async_queue:
            ioloop.IOLoop.instance().stop()

    def get(self, path='me', fql=None, connection_type=None, metadata=False,
            format='json'):
        token_url = self._create_token_url(path, fql, connection_type, metadata,
                                           format)
        try:
            response = simplejson.load(urllib.urlopen(token_url))
        except Exception, e:
            logging.error(e)
            return HttpResponseServerError

        if 'error' in response:
            return self._error_handler(response, fql, token_url)
        elif 'data' in response:
            return response['data']
        return response

    def _error_handler(self, response, fql, url):
        error = response['error']
        logging.error(error)
        if fql: logging.error(fql)
        if url: logging.error(url)

        auth_error_codes = [190]
        auth_error_codes.extend(range(400, 500)) # Error codes between 400 and 499
        if 'code' in error:
            error_code = error['code']
            if error_code in auth_error_codes:
                raise FacebookSessionError(error)
        raise FacebookGenericError(error)

    def _create_token_url(self, path, fql, connection_type, metadata, format):
        token_url = '%s%s' % (settings.GRAPH_API_URL, path)
        if connection_type:
            token_url = '%s/%s' % (token_url, connection_type)
        params = {'access_token': self.access_token,
                  'format': format}
        if metadata:
            params['metadata'] = 'true'
        if fql:
            params['q'] = fql

        token_url = '%s?%s' % (token_url, urllib.urlencode(params))
        return token_url

class ExampleAPI(GraphAPI):
    def get_significant_other(self):
        fql = '''select name, uid from user where uid in 
        (select significant_other_id from user where uid=me())'''
        query = self.get(path='fql', fql=fql)
        return query

    def get_upcoming_birthdates(self):
        today = dict(day=datetime.datetime.now().strftime('%2d'),
                     month=datetime.datetime.now().strftime('%2m'))
        fql = '''select name, uid, birthday_date, pic_small, pic, pic_big 
        from user where uid in 
        (select uid2 from friend where uid1=me()) 
        and strlen(birthday_date) != 0 
        and ((substr(birthday_date, 0, 2) = {month}
        and substr(birthday_date, 3, 5) > {day})) 
        order by birthday_date limit 7'''.format(**today)
        query = self.get(path='fql', fql=fql)
        return query

    def get_family_birthdates(self):
        fql = '''select name, birthday_date, relationship_status, 
        significant_other_id, family from user where uid = me()'''
        query = self.get(path='fql', fql=fql)
        return query

