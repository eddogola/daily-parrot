from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.urls import reverse, reverse_lazy

from main import models, forms

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
        #suggestions = models.BlogPost.objects.topic_suggestions(topic, 3).\
        #    exclude(self.object)
        #ctx['topic_suggestions'] = suggestions
        if self.request.user.is_authenticated:
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
    
class BlogPostCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.BlogPostForm
    template_name = 'blog_post_create.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        form.instance.slug = slugify(form.instance.title)
        form.instance.views = 0
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tags = models.Tag.objects.all()
        topics = models.Topic.objects.all()
        ctx['tags'] = tags
        ctx['topics'] = topics
        return ctx
    
class EditProfileView(LoginRequiredMixin, FormView):
    form_class = forms.ProfileForm
    template_name = 'edit_profile.html'
    
    def get_initial(self):
        init = super().get_initial()
        init['first_name'] = self.request.user.first_name
        init['last_name'] = self.request.user.last_name
        init['username'] = self.request.user.username
        init['email'] = self.request.user.email
        init['bio'] = self.request.user.profile.bio
        init['avatar'] = self.request.user.profile.avatar
        
        return init
    
    def form_valid(self, form):
        user_data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'username': form.cleaned_data['username'],
            'email': form.cleaned_data['email'],
        }
        profile_data = {
            'bio': form.cleaned_data['bio'],
            'avatar': form.cleaned_data['avatar'],
        }
        
        for attr, value in user_data.items():
            setattr(self.request.user, attr, value)
            
        for attr, value in profile_data.items():
            setattr(self.request.user.profile, attr, value)
            
        self.request.user.save()
        self.request.user.profile.save()
        return self.get_success_url()
        
    def get_success_url(self):
        return redirect(reverse_lazy('profile',  args=[self.request.user.username]))