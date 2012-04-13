from django.contrib.auth import models as auth_models
from models import Token
from graph_api import GraphAPI

class FacebookBackend:
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False
    def authenticate(self, session):
        api = GraphAPI(session.access_token)
        profile = api.get()
        id = profile['id']
        try:
            user = auth_models.User.objects.get(username=id)
        except auth_models.User.DoesNotExist:
            user = auth_models.User(username=id)

        user.set_unusable_password()
        if 'email' in profile:
            user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.save()

        try:
            token = Token.objects.get(uid=id, user=user)
        except Exception:
            token = Token(uid=id, user=user)
        token.access_token = session.access_token
        token.expires = session.expires
        token.save()

        return user

    def get_user(self, user_id):
        try:
            return auth_models.User.objects.get(pk=user_id)
        except auth_models.User.DoesNotExist:
            return None
