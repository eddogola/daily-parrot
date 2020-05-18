from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.conf import settings
from uuid import uuid4
from random import sample
import os

class Tag(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField(unique=True, max_length=15)
    
    def __str__(self):
        return self.name
    
class Classification(models.Model):
    name = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    tagline = models.CharField(max_length=20, null=True)
    classification = models.ForeignKey(Classification, on_delete=models.PROTECT,
                                       related_name='topics')
    banner = models.ImageField(upload_to='topic-banners', null=True)
    
    def __str__(self):
        return self.name

class Follow(models.Model):
    follower = models.ForeignKey('Profile', related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey('Profile', related_name='followers', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']

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
    
    def is_following_topic(self, topic):
        return topic in self.topics.all()
    
    def follow_topic(self, topic):
        if not self.is_following_topic(topic):
            self.topics.add(topic)
            self.save()
            return True
        return False
        
    def unfollow_topic(self, topic):
        if self.is_following_topic(topic):
            self.topics.remove(topic)
            self.save()
            return True
        return False
    
    def is_following_profile(self, profile):
        try:
            follow = Follow.objects.get(follower=self, following=profile)
            return follow in self.following.all()
        except Follow.DoesNotExist:
            return False
    
    def follow_profile(self, profile):
        if not self.is_following_profile(profile) and self.id != profile.id:
            Follow.objects.create(follower=self, following=profile)
            return True
        return False
    
    def unfollow_profile(self, profile):
        if self.is_following_profile(profile):
            follow = Follow.objects.get(follower=self, following=profile)
            follow.delete()
            return True
        return False
    
    def __str__(self):
        return self.user.email

class BlogPostManager(models.Manager):
    
    def active(self):
        return self.filter(active=True)
    
    def topic_suggestions(self, topic, max=3):
        qs = self.active().filter(topic=topic)
        qs = sample(list(qs.all()), max)
        return qs

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
    views = models.PositiveIntegerField()
    
    objects = BlogPostManager()
    
    class Meta:
        ordering = ['created']
    
    def __str__(self):
        return self.title