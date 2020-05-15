from django.contrib import admin

from main import models

class BlogPostsInline(admin.TabularInline):
    model = models.BlogPost.tags.through

class TagsInline(admin.TabularInline):
    model = models.BlogPost.tags.through

@admin.register(models.Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'blog_posts',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    
    def blog_posts(self, obj):
        blog_posts_count = obj.blog_posts.count()
        return blog_posts_count
    
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (
        BlogPostsInline,
    )
    
@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created', 'updated', 'author', 'classification', 'active',)
    list_editable = ('active',)
    search_fields = ('title', 'body', 'author',)
    list_filter = ('active', 'created', 'updated',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (
        TagsInline,
    )