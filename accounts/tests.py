from django.test import TestCase
from django.contrib.auth import get_user_model

class CustomUserTests(TestCase):
    
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