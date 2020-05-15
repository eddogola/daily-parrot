from django.db import models
from uuid import uuid4

from accounts.models import Profile

class Classification(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField(unique=True, max_length=15)
    
    def __str__(self):
        return self.name

class BlogPostManager(models.Manager):
    
    def active(self):
        return self.filter(active=True)

class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4(), editable=False)
    slug = models.SlugField()
    title = models.CharField(max_length=140, unique=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    banner = models.ImageField(upload_to='blog-posts-banners')
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='blog_posts')
    classification = models.ForeignKey(Classification, on_delete=models.PROTECT,
                                       related_name='blog_posts')
    tags = models.ManyToManyField(Tag, related_name='blog_posts')
    active = models.BooleanField(default=True)
    
    objects = BlogPostManager()
    
    def __str__(self):
        return self.title