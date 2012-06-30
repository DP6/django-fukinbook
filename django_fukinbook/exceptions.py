class FacebookGenericError(Exception):
    def __init__(self, error):
        self.type = error.get('type')
        self.message = error.get('message')
        self.code = error.get('code')

    def __str__(self):
        return u'%s (#%s): "%s"' % (self.type, self.code, self.message)

class FacebookSessionError(FacebookGenericError):
    pass
