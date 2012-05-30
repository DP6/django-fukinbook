from django.http import HttpResponseServerError
import logging
from django.conf import settings
from exceptions import FacebookGenericError
import simplejson
import urllib
import urlparse

class FacebookSession:
    TOKEN_URI = 'oauth/access_token'
    ARGS = {
        'client_id': settings.FACEBOOK_APP_ID,
        'client_secret': settings.FACEBOOK_APP_SECRET,
        'redirect_uri': settings.FACEBOOK_REDIRECT_URI}

    def __init__(self, code):
        self.code = code
        self.access_token = None
        self.expires = None
        self._get_response()

    def _encode_url(self):
        self.ARGS['code'] = self.code
        return '%s%s?%s' % (settings.GRAPH_API_URL, self.TOKEN_URI, 
                            urllib.urlencode(self.ARGS))

    def _get_response(self):
        url = self._encode_url()
        try:
            response = urlparse.parse_qs(urllib.urlopen(url).read())
            self.access_token = response['access_token'][0]
            self.expires = response['expires'][0]
        except KeyError, e:
            logging.error(e)
            raise FacebookGenericError(str(e))
        except Exception, e:
            logging.error(e)
            return HttpResponseServerError
            
        
