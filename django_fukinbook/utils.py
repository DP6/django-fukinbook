import urllib
import settings

def create_authorize_url(redirect_uri=settings.FACEBOOK_REDIRECT_URI):
    AUTH_URI = 'oauth/authorize'
    
    params = {
      'client_id': settings.FACEBOOK_APP_ID,
      'redirect_uri': redirect_uri,
      'scope': settings.FACEBOOK_APP_SCOPE,
      'popup': 'true'}
    authorize_url = '%s%s?%s' % (settings.GRAPH_API_URL, AUTH_URI, 
                                 urllib.urlencode(params))
    return authorize_url