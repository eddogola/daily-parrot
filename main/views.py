from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from main import models

class TopicsListView(ListView):
    model = models.Classification
    context_object_name = 'classifications'
    template_name = 'topics.html'
    
class TopicDetailView(DetailView):
    template_name = 'topic.html'
    
    def get_object(self):
        obj = get_object_or_404(models.Topic, slug=self.kwargs['topic_slug'])
        return obj
    
class ProfileDetailView(DetailView):
    template_name = 'profile.html'
    
    def get_object(self):
        username = self.kwargs['username']
        user = get_object_or_404(get_user_model(), username=username)
        obj = get_object_or_404(models.Profile, user=user)
        return obj
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        is_following = self.request.user.profile.\
            is_following_profile(self.object)
        ctx['is_following'] = is_following
        return ctx
    
class BlogPostDetailView(DetailView):
    template_name = 'blog_post.html'
    
    def get_object(self):
        blog_post_slug = self.kwargs['blog_post_slug']
        obj = models.BlogPost.objects.active().get(slug=blog_post_slug)
        return obj
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topic = self.object.topic
        suggestions = models.BlogPost.objects.topic_suggestions(topic, 3).\
            exclude(self.object)
        ctx['topic_suggestions'] = suggestions
        
        is_following = self.request.user.profile.\
            is_following_profile(self.object.author)
        ctx['is_following'] = is_following
        return ctx

@login_required
def follow_topic(request, topic_slug):
    topic = get_object_or_404(
        models.Topic, slug=topic_slug
    )
    profile = request.user.profile
    profile.follow_topic(topic)
    return redirect(reverse('topic', args=[topic.slug]))

@login_required
def unfollow_topic(request, topic_slug):
    topic = get_object_or_404(
        models.Topic, slug=topic_slug
    )
    profile = request.user.profile
    profile.unfollow_topic(topic)
    return redirect(reverse('topic', args=[topic.slug]))

@login_required
def follow_profile(request, username):
    user = get_user_model().objects.get(username=username)
    profile = get_object_or_404(models.Profile, user=user)
    #actual following
    request.user.profile.follow_profile(profile)
    return redirect(reverse('profile', args=[username]))

@login_required
def unfollow_profile(request, username):
    user = get_user_model().objects.get(username=username)
    profile = get_object_or_404(models.Profile, user=user)
    #actual unfollowing
    request.user.profile.unfollow_profile(profile)
    return redirect(reverse('profile', args=[username]))
    