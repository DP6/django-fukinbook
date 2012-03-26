

def get(path='me', connection_type=None, metadata=False):
	url = '%s%s' % (self.API_URL, object_id)
    if connection_type:
        url += '/%s' % (connection_type)

    params = {'access_token': self.access_token}
    if metadata:
        params['metadata'] = 1

    url += '?%s' % urllib.urlencode(params)
    response = simplejson.load(urllib.urlopen(url))
    if 'error' in response:
        error = response['error']
        raise FacebookSessionError(error['type'], error['message'])
    return response