from django.http import Http404
from django.shortcuts import redirect
from session import FacebookSessionError
from settings import LOGGER as logger
import logging
import settings
import simplejson
import urllib
import urlparse

class GraphAPI:
    ''' We are supposing that every request will have a session '''
    # TODO: Implement anon requests
    def __init__(self, access_token=None):
        self.access_token = access_token
    
    def get(self, path='me', fql=None, connection_type=None, metadata=False, 
            format='json'):
        token_url = self._create_token_url(path, fql, connection_type, metadata, 
                                           format)
        try:
            response = simplejson.load(urllib.urlopen(token_url))
        except Exception, e:
            # TODO: Need to know what to do with exception
            logger.error(e)
            raise Http404
        if 'error' in response:
            return self._error_handler(response)
        return response
    
    def _error_handler(self, response):
        error = response['error']
        logger.error(error)
        
        raise FacebookSessionError(error['type'], error['message'])
    
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
        fql = '''select name, uid, birthday_date from user where uid in 
        (select uid2 from friend where uid1=me()) 
        and strlen(birthday_date) != 0 
        and ((substr(birthday_date, 0, 2) = 03 
        and substr(birthday_date, 3, 5) > 26) 
        or (substr(birthday_date, 0, 2) = 05 
        and substr(birthday_date, 3, 5) < 26)) 
        order by birthday_date limit 5'''
        query = self.get(path='fql', fql=fql)
        return query

    def get_family_birthdates(self):
        fql = '''select name, birthday_date, relationship_status, 
        significant_other_id, family from user where uid = me()'''
        query = self.get(path='fql', fql=fql)
        return query
        
        