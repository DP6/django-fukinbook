from django.contrib.auth import models as auth_models

import models

class FacebookBackend:
    supports_object_permissions=True 
    supports_anonymous_user=False
    def authenticate(self, token=None):
        facebook_session = models.FacebookSession.objects.get(
            access_token=token,
        )

        profile = facebook_session.query('me')
        
        try:
            user = auth_models.User.objects.get(username=profile['id'])
        except auth_models.User.DoesNotExist:
            user = auth_models.User(username=profile['id'])
    
        user.set_unusable_password()
        user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.save()

        try:
            models.FacebookSession.objects.get(uid=profile['id']).delete()
        except models.FacebookSession.DoesNotExist:
            pass

        facebook_session.uid = profile['id']
        facebook_session.user = user
        facebook_session.save()
   
        return user
   
    def get_user(self, user_id):

        try:
            return auth_models.User.objects.get(pk=user_id)
        except auth_models.User.DoesNotExist:
            return None
