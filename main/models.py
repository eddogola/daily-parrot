from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.conf import settings
from uuid import uuid4
import os

class Tag(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField(unique=True, max_length=15)
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    tagline = models.CharField(max_length=20, null=True)
    banner = models.ImageField(upload_to='topic-banners', null=True)
    
    def __str__(self):
        return self.name

def avatar_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'avatars/{0}/{1}{2}'.format(instance.id, uuid4(), ext)
    
class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to=avatar_path,
        default=ImageFile(
            open(os.path.join(settings.MEDIA_ROOT, 'avatars/default.png'), 'rb')
        ))
    bio = models.CharField(max_length=50, blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True)
    topics = models.ManyToManyField(Topic, related_name='profiles')
    
    def __str__(self):
        return self.user.email

class BlogPostManager(models.Manager):
    
    def active(self):
        return self.filter(active=True)

class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4(), editable=False)
    slug = models.SlugField()
    title = models.CharField(max_length=140, unique=True)
    tagline = models.CharField(max_length=50, null=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    banner = models.ImageField(upload_to='blog-posts-banners')
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='blog_posts')
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT,
                                       related_name='blog_posts')
    tags = models.ManyToManyField(Tag, related_name='blog_posts')
    active = models.BooleanField(default=True)
    
    objects = BlogPostManager()
    
    def __str__(self):
        return self.title