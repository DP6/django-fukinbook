from django.contrib.auth.models import User
from models import Token, UserProfile
from graph_api import GraphAPI
import logging
from django.contrib.auth import logout
from django.db.transaction import commit_on_success


class FacebookBackend:
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    @commit_on_success
    def _save_user(self, fb_profile):
        uid = fb_profile.get('uid')
        try:
            user = User.objects.get(username=uid)
        except User.DoesNotExist:
            user = User(username=uid)
        user.set_unusable_password()
        user.email = fb_profile.get('email')
        if not user.email:
            user.email = 'none@none.com'
        user.first_name = fb_profile.get('first_name')
        user.last_name = fb_profile.get('last_name')
        user.save()

        user_profile = user.get_profile()
        user_profile.is_app_user = True
        user_profile.save()

        return user

    def _save_token(self, session, user):
        uid = user.username
        try:
            token = Token.objects.get(uid=uid, user=user)
        except Exception:
            token = Token(uid=uid, user=user)
        token.access_token = session.access_token
        token.expires = session.expires
        token.save()

        return token

    def authenticate(self, session):
        api = GraphAPI(session.access_token)
        fql = '''
        SELECT uid, email, first_name, last_name, pic_big, 
        pic, pic_small, pic_square FROM user WHERE uid = me()'''
        fb_profile = api.get(path='fql', fql=fql)[0]

        user = self._save_user(fb_profile)
        token = self._save_token(session, user)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
