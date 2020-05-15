from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.conf import settings
from django.urls import reverse
import os

from . import models

class ModelTests(TestCase):
    
    def test_custom_user(self):
        user = get_user_model().objects.create_user(
            'testuser@email.com', 'mypass123')
        
        self.assertTrue(get_user_model().objects.filter(email='testuser@email.com').exists())
        user.refresh_from_db()
        self.assertFalse(user.is_staff and user.is_superuser)
        
    def test_custom_superuser(self):
        user = get_user_model().objects.create_superuser(
            'testadmin@email.com', 'mypass123')
        user.refresh_from_db()
        
        self.assertTrue(user.is_staff and user.is_superuser)
    
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
        
class ViewTests(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'myuser@email.com', 'testpass123'
        )
    
    def test_login_view(self):
        #test get request
        resp = self.client.get(reverse('login'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Welcome Back')
        self.assertTemplateUsed(resp, 'registration/login.html')
        
        #test post request(invalid credentials)
        invalid_post_data = {
            'username':'testmail@mail.me',
            'password':'wrongpass123'
        }
        invalid_post_resp = self.client.post(reverse('login'),
                                             invalid_post_data)
        self.assertContains(invalid_post_resp, 'Please enter a correct email address and password')
        
        #test post request(valid credentials)
        valid_post_data = {
            'username':'myuser@email.com',
            'password':'testpass123'
        }
        valid_post_resp = self.client.post(reverse('login'),
                                           valid_post_data, follow=True)
        self.assertEqual(valid_post_resp.status_code, 200)
        self.assertNotContains(valid_post_resp, 'Please enter a correct email address and password')
        self.assertContains(valid_post_resp, 'Change password')
        
    def test_signup_view(self):
        #test get request
        resp = self.client.get(reverse('signup'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'The world is all about stories')
        self.assertTemplateUsed(resp, 'registration/signup.html')
        
        #test invalid post data
        invalid_post_data = {
            'first_name':'John',
            'last_name':'Doe',
            'email':'john@doe.me',
            'password1':'testpass123',
            'password2':'testpass345',
        }
        invalid_resp = self.client.post(reverse('signup'),
                                        invalid_post_data)
        self.assertTrue(invalid_resp.status_code, 200)
        self.assertContains(invalid_resp, "The two password fields")
        
        #test valid post_data
        valid_post_data = {
            'first_name':'John',
            'last_name':'Doe',
            'email':'john@doe.me',
            'password1':'testpass123',
            'password2':'testpass123',
        }
        valid_resp = self.client.post(reverse('signup'),
                                      valid_post_data)
        self.assertRedirects(valid_resp, reverse('login'))

        valid_post_data.update({'email':'jane@doe.me'})
        valid_resp1 = self.client.post(reverse('signup'),
                                      valid_post_data, follow=True)
        self.assertContains(valid_resp1, 'you may now sign up.')
        