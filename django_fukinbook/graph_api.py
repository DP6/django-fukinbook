from session import FacebookSessionError, 

# TODO: API_URL is duplicated with session module. Fix it.
class GraphAPI():
    API_URL = 'https://graph.facebook.com/'
    def __init__(self, session=None):
        self.session = session
        
    def get(self, path='me', connection_type=None, metadata=False):
        url = '%s%s' % (self.API_URL, path)
        if connection_type:
            url += '/%s' % (connection_type)

        params = {'access_token': self.session.access_token}
        if metadata:
            params['metadata'] = 1

        url += '?%s' % urllib.urlencode(params)
        response = simplejson.load(urllib.urlopen(url))
        if 'error' in response:
            error = response['error']
            raise FacebookSessionError(error['type'], error['message'])
        return response