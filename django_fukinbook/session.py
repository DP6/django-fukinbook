from django.http import HttpResponseRedirect

import urlparse
import urllib
import simplejson

import settings

class FacebookSessionError(Exception):
    def __init__(self, error_type, message):
        self.message = message
        self.type = error_type

    def get_message(self):
        return self.message

    def get_type(self):
        return self.type

    def __unicode__(self):
        return u'%s: "%s"' % (self.type, self.message)

# TODO: API_URL is duplicated with graph_api module. Fix it.
class FacebookSession:
    API_URL = 'https://graph.facebook.com/'
    TOKEN_URL = '%s%s' % (API_URL, 'oauth/access_token?')
    ARGS = {
        'client_id': settings.FACEBOOK_APP_ID,
        'client_secret': settings.FACEBOOK_APP_SECRET,
        'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
    }

    def __init__(self, code):
        self.code = code
        self.access_token = None
        self.expires = None
        self._get_response()

    def _encode_url(self):
        self.ARGS['code'] = self.code
        return '%s%s' % (self.TOKEN_URL, urllib.urlencode(self.ARGS))

    def _get_response(self):
        url = self._encode_url()
        try:
            response = urlparse.parse_qs(urllib.urlopen(url).read())
        except Exception, e:
            # TODO: Need to know what to do with exception
            HttpResponseRedirect('/404/')
        self.access_token = response['access_token'][0]
        self.expires = response['expires'][0]

#    def get_user_profile(self, object_id='me', connection_type=None,
#                         metadata=False):
#        url = '%s%s' % (self.API_URL, object_id)
#        if connection_type:
#            url += '/%s' % (connection_type)
#
#        params = {'access_token': self.access_token}
#        if metadata:
#            params['metadata'] = 1
#
#        url += '?%s' % urllib.urlencode(params)
#        try:
#            response = simplejson.load(urllib.urlopen(url))
#        except Exception, e:
#            # TODO: Need to know what to do with exception
#            HttpResponseRedirect('/404/')
#        if 'error' in response:
#            error = response['error']
#            raise FacebookSessionError(error['type'], error['message'])
#        return response