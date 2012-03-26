from session import FacebookSessionError

import urlparse
import urllib
import simplejson

# TODO: API_URL is duplicated with session module. Fix it.
class GraphAPI:
    ''' We are supposing that every request will have a session '''
    # TODO: Implement anon requests
    API_URL = 'https://graph.facebook.com/'
    def __init__(self, access_token=None):
        self.access_token = access_token
        
    def get(self, path='me', connection_type=None, metadata=False):
        url = '%s%s' % (self.API_URL, path)
        if connection_type:
            url += '/%s' % (connection_type)

        params = {'access_token': self.access_token}
        if metadata:
            params['metadata'] = 1

        url += '?%s' % urllib.urlencode(params)
        try:
            response = simplejson.load(urllib.urlopen(url))
        except Exception, e:
            # TODO: Need to know what to do with exception
            HttpResponseRedirect('/404/')
        if 'error' in response:
            error = response['error']
            raise FacebookSessionError(error['type'], error['message'])
        return response
