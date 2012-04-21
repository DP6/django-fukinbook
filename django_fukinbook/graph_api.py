from django.http import HttpResponseServerError
from exceptions import FacebookGenericError, FacebookSessionError
from django.conf import settings
import logging
import simplejson
import urllib
import datetime

class GraphAPI:
    ''' We are supposing that every request will have a session '''
    def __init__(self, access_token=None):
        self.access_token = access_token
    
    def get(self, path='me', fql=None, connection_type=None, metadata=False, 
            format='json'):
        token_url = self._create_token_url(path, fql, connection_type, metadata, 
                                           format)
        try:
            response = simplejson.load(urllib.urlopen(token_url))
        except Exception, e:
            logging.error(e)
            raise HttpResponseServerError(str(e))
        
        if 'error' in response:
            return self._error_handler(response)
        elif 'data' in response:
            return response['data']
        return response
    
    def _error_handler(self, response):
        error = response['error']
        logging.error(error)
        
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
        
        