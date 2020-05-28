from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.conf import settings
import os.path
import json

from main import models

class Command(BaseCommand):
    help = 'import data fixtures'
    
    def handle(self, *args, **kwargs):
        fixture = open(os.path.join(settings.BASE_DIR, 'fixtures/fix.json'))
        parsed = json.loads(fixture.read())

        user_count = 0
        class_count = 0
        tags_count = 0
        topics_count = 0
        profiles_count = 0
        posts_count = 0

        for row in parsed:
            model = row['model']
            fields = row['fields']
            
            if model == 'accounts.user':
                if not get_user_model().objects.filter(username=fields['username']).exists():
                    del fields['groups']
                    del fields['user_permissions']
                    user = get_user_model().objects.create(**fields)
                    print('User ', user.username, ' added')
                    user_count += 1
            
            if model == 'main.classification':
                if not models.Classification.objects.filter(name=fields['name']).exists():
                    classification = models.Classification.objects.create(**fields)
                    print('Classification ', classification.name, ' added')
                    class_count += 1
            
            if model == 'main.tag':
                if not models.Tag.objects.filter(slug=fields['slug']).exists():
                    tag = models.Tag.objects.create(**fields)
                    print('Tag ', tag.name, ' added')
                    tags_count += 1
                
            if model == 'main.topic':
                if not models.Topic.objects.filter(slug=fields['slug']).exists():
                    topic = models.Topic.objects.create(
                    name=fields['name'],
                    slug=fields['slug'],
                    tagline=fields['tagline'],
                    banner=ImageFile(
                        open(
                            os.path.join(settings.MEDIA_ROOT, fields['banner']), 'rb'
                        )),
                    classification=models.Classification.objects.get(name=fields['classification'])
                    )
                    print('Topic ', topic.name, ' added')
            
            if model == 'main.profile':
                
                if not models.Profile.objects.filter(user__email=fields['user'][0]).exists():
                    profile = models.Profile.objects.create(
                    user=get_user_model().objects.get(
                        email=fields['user'][0]
                    ),
                    avatar=ImageFile(
                        open(
                            os.path.join(settings.MEDIA_ROOT, fields['avatar']),'rb'
                        )),
                    bio=fields['bio'],
                    joined=fields['joined'],
                    confirmed=fields['confirmed']
                    )
                    print('Profile ', profile.user.username, ' added')
                    profiles_count += 1
            
            if model == 'main.blogpost':
                
                if not models.BlogPost.objects.filter(slug=fields['slug']).exists():
                    post = models.BlogPost.objects.create(
                    slug=fields['slug'],
                    title=fields['title'],
                    tagline=fields['tagline'],
                    body=fields['body'],
                    created=fields['created'],
                    banner=ImageFile(
                        open(
                            os.path.join(settings.MEDIA_ROOT, fields['banner']), 'rb'
                        )),
                    topic=models.Topic.objects.get(slug=fields['topic']),
                    active=fields['active'],
                    thumbs_up=fields['thumbs_up'],
                    thumbs_down=fields['thumbs_down'],
                    author=models.Profile.objects.get(user__username=fields['author'])
                    )
                    print('Blog Post ', post.title, ' added')
                    posts_count += 1
                    
        self.stdout.write(self.style.SUCCESS(str(user_count) + ' users added'))
        self.stdout.write(self.style.SUCCESS(str(class_count) + ' classifications added'))
        self.stdout.write(self.style.SUCCESS(str(tags_count) + ' tags added'))
        self.stdout.write(self.style.SUCCESS(str(topics_count) + ' topics added'))
        self.stdout.write(self.style.SUCCESS(str(profiles_count) + ' profiles added'))
        self.stdout.write(self.style.SUCCESS(str(posts_count) + ' posts added'))
              