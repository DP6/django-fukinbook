from session import FacebookSessionError

import urlparse
import urllib
import simplejson
import pprint

# TODO: API_URL is duplicated with session module. Fix it.
class GraphAPI:
    ''' We are supposing that every request will have a session '''
    # TODO: Implement anon requests
    API_URL = 'https://graph.facebook.com/'
    def __init__(self, access_token=None):
        self.access_token = access_token
        
    def get(self, path='me', fql=None, connection_type=None, metadata=False, format='json'):
        url = '%s%s' % (self.API_URL, path)
        if connection_type:
            url += '/%s' % (connection_type)

        params = {'access_token': self.access_token,
                  'format': format}
        if metadata:
            params['metadata'] = 1
        if fql:
            params['q'] = fql

        url += '?%s' % urllib.urlencode(params)
        pp = pprint.PrettyPrinter()
        pp.pprint(url)
        try:
            response = simplejson.load(urllib.urlopen(url))
        except Exception, e:
            # TODO: Need to know what to do with exception
            HttpResponseRedirect('/404/')
        if 'error' in response:
            error = response['error']
            raise FacebookSessionError(error['type'], error['message'])
        return response

    def get_significant_other(self, object_id='me'):
        user = self.get(path=object_id)
        if 'significant_other' in user:
            significant_other = user['significant_other']
            return significant_other
        return None
    
    def get_upcoming_birthdates(self):
        #fql = 'select name, uid, birthday_date from user where uid in (select uid2 from friend where uid1=me()) and strlen(birthday_date) != 0 and ((substr(birthday_date, 0, 2) = 03 and substr(birthday_date, 3, 5) > 26) or (substr(birthday_date, 0, 2) = 05 and substr(birthday_date, 3, 5) < 26)) order by birthday_date'
        #fql = 'select name, uid, birthday_date from user where uid in (select uid2 from friend where uid1=me())'
        fql = '''select name, uid, birthday_date from user where uid in (select uid2 from friend where uid1=me()) and strlen(birthday_date) != 0 and ((substr(birthday_date, 0, 2) = '03' and substr(birthday_date, 3, 5) > '26') or (substr(birthday_date, 0, 2) = '05' and substr(birthday_date, 3, 5) < '26')) order by birthday_date limit 5'''
        response = self.get(path='fql', fql=fql)
        return response
        
        