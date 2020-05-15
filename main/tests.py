from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
import os

from . import models

class ModelTests(TestCase):
    
    def test_profile_model(self):
        user = get_user_model().objects.create_user(
            'myuser@email.com', 'testpass123'
        )
        profile = models.Profile.objects.create(
            user=user
        )
        user.refresh_from_db()
        
        self.assertEqual(user.profile, profile)
        self.assertEqual(profile.user.email, 'myuser@email.com')
        
        #test default avatar
        default_avatar = open(os.path.join(settings.MEDIA_ROOT, 'avatars/default.png'), 'rb').read()
        self.assertEqual(profile.avatar.read(), default_avatar)
        
    def tearDown(self):
        for profile in models.Profile.objects.all():
            try:
                profile.avatar.delete(save=False)
                os.rmdir(os.path.join(settings.MEDIA_ROOT, 'avatars/{}'.format(profile.id)))
            except:
                pass
        super().tearDown()