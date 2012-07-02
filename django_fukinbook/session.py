from django.http import HttpResponseServerError
import logging
from django.conf import settings
from exceptions import FacebookGenericError
import simplejson
import urllib
import urlparse
import httplib2


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
        self._get_token_from_response(self._encode_token_url)
#        self._get_token_from_response(self._encode_extended_token_url)

    def _encode_token_url(self):
        ARGS = dict(self.ARGS)
        ARGS['code'] = self.code
        return '%s%s?%s' % (settings.GRAPH_API_URL, self.TOKEN_URI,
                            urllib.urlencode(ARGS))

    def _encode_extended_token_url(self):
        ARGS = dict(self.ARGS)
        ARGS['grant_type'] = 'fb_exchange_token'
        ARGS['fb_exchange_token'] = self.access_token
        return '{0}{1}?{2}'.format(settings.GRAPH_API_URL, self.TOKEN_URI,
                                   urllib.urlencode(ARGS))

    def _get_token_from_response(self, token_generator_func):
        url = token_generator_func()
        logging.debug(url)
        h = httplib2.Http()
        try:
            headers, response = h.request(url, 'GET')
            response = urlparse.parse_qs(response)
            self.access_token = response['access_token'][0]
            self.expires = response['expires'][0]
        except KeyError, e:
            logging.error(e)
            raise FacebookGenericError(str(e))
        except Exception, e:
            logging.error(e)
            return HttpResponseServerError





