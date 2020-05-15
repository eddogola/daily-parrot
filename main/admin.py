from django.contrib import admin
from django.utils.html import format_html

from main import models

class BlogPostsInline(admin.TabularInline):
    model = models.BlogPost

class BlogPostsTagsInline(admin.TabularInline):
    model = models.BlogPost.tags.through
    
class ProfileTopicsInline(admin.TabularInline):
    model = models.Profile.topics.through

@admin.register(models.Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline','slug', 'blog_posts', 'get_banner',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = (
        ProfileTopicsInline,
    )
    
    def blog_posts(self, obj):
        blog_posts_count = obj.blog_posts.count()
        return blog_posts_count
    
    def get_banner(self, obj):
        return format_html(
            "<img src='{}'>".format(obj.banner.url)
        )
    
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (
        BlogPostsTagsInline,
    )
    
@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title','tagline', 'slug', 'topic', 'author', 'created',
                     'updated', 'active', 'get_banner')
    list_editable = ('active',)
    search_fields = ('title', 'body', 'author',)
    list_filter = ('active', 'created', 'updated',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (
        BlogPostsTagsInline,
    )
    
    def get_banner(self, obj):
        return format_html(
            "<img src='{}'>".format(obj.banner.url)
        )

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_avatar',)
    inlines = (
        BlogPostsInline,
        ProfileTopicsInline,
    )

    def get_email(self, obj):
        return obj.user.email
    
    def get_avatar(self, obj):
        return format_html(
            '<img src="{}">'.format(obj.avatar.url)
        )
