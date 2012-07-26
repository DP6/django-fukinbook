from django.contrib.auth.models import User
from models import UserProfile
from graph_api import GraphAPI
import logging
from django.contrib.auth import logout
from django.db.transaction import commit_on_success


class FacebookBackend:
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    @commit_on_success
    def _save_fb_user(self, user, fb_profile):

        user.email = fb_profile.get('email')
        if not user.email:
            user.email = 'none@none.com'
        user.first_name = fb_profile.get('first_name')
        user.last_name = fb_profile.get('last_name')
        user.save()

        user_profile = user.get_profile()
        user_profile.is_app_user = True
        user_profile.uid = fb_profile.get('uid')
        user_profile.save()

        return user

    def _save_token(self, facebook_session, django_session, user):
        django_session['fb_token'] = {'access_token': facebook_session.access_token,
                                      'expires': facebook_session.expires}

    def authenticate(self, facebook_session, django_session, user=None):
        api = GraphAPI(facebook_session.access_token)
        fql = '''
            SELECT uid, username, email, first_name, last_name 
            FROM user WHERE uid = me()'''
        fb_profile = api.get(path='fql', fql=fql)[0]

        if user and user.is_active:
            user = self._save_fb_user(user, fb_profile)
        else:
            user = User.objects.get_or_create(username=fb_profile['username'])[0]
            user.set_unusable_password()
            user = self._save_fb_user(user, fb_profile)

        self._save_token(facebook_session, django_session, user)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
