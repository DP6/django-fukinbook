from session import FacebookSessionError
from django.shortcuts import redirect
import simplejson
import urllib
import urlparse
import settings
import logging

logger = logging.getLogger('fukinbook.custom')

class GraphAPI:
    ''' We are supposing that every request will have a session '''
    # TODO: Implement anon requests
    def __init__(self, access_token=None):
        self.access_token = access_token
    
    def _create_token_url(self, path, fql, connection_type, metadata, format):
        token_url = '%s%s' % (settings.GRAPH_API_URL, path)
        if connection_type:
            token_url = '%s/%s' % (token_url, connection_type)
        params = {'access_token': self.access_token,
                  'format': format}
        if metadata:
            params['metadata'] = 1
        if fql:
            params['q'] = fql

        token_url = '%s?%s' % (token_url, urllib.urlencode(params))
        return token_url
        
    def get(self, path='me', fql=None, connection_type=None, metadata=False, 
            format='json'):
        refresh_uri = '/login/?refresh_token=true'
        token_url = self._create_token_url(path, fql, connection_type, metadata, 
                                           format)
        try:
            response = simplejson.load(urllib.urlopen(token_url))
        except Exception, e:
            # TODO: Need to know what to do with exception
            return redirect('/404/')
        if 'error' in response:
            error = response['error']
            # TODO: This if above need ALOT more tests
            # I can't predict OAuthException can be fixed just only refreshing
            # the access token
            if error['type'] == 'OAuthException':
                return redirect(refresh_uri)
            raise FacebookSessionError(error['type'], error['message'])
        return response

    def get_significant_other(self, object_id='me'):
        user = self.get(path=object_id)
        if 'significant_other' in user:
            significant_other = user['significant_other']
            return significant_other
        return user
    
    def get_upcoming_birthdates(self):
        fql = '''select name, uid, birthday_date from user where uid in 
        (select uid2 from friend where uid1=me()) 
        and strlen(birthday_date) != 0 
        and ((substr(birthday_date, 0, 2) = 03 
        and substr(birthday_date, 3, 5) > 26) 
        or (substr(birthday_date, 0, 2) = 05 
        and substr(birthday_date, 3, 5) < 26)) 
        order by birthday_date limit 5'''
        response = self.get(path='fql', fql=fql)
        return response
        
        