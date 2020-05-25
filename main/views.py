from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.db.models import Sum
from random import sample

from main import models, forms

class HomePageView(TemplateView):
    template_name = 'home.html'
    PER_PAGE = 20
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            authors = models.Profile.objects.exclude(pk=self.request.user.profile.pk).\
                    annotate(rating=Sum('blog_posts__thumbs_up')).order_by('rating')
            following_posts = user.profile.get_following_posts()
            posts_list = models.BlogPost.objects.exclude(
                id__in=[p.pk for p in following_posts]).exclude(author=user.profile)
            posts_list = following_posts + list(posts_list)
        else:
            authors = models.Profile.objects.annotate(rating=Sum('blog_posts__thumbs_up')).order_by('rating')
            posts_list = models.BlogPost.objects.active()
        paginator = Paginator(posts_list, self.PER_PAGE)
        page = self.request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        ctx['authors'] = authors[:3]
        ctx['posts'] = posts
        return ctx    

class TopicsListView(ListView):
    model = models.Classification
    context_object_name = 'classifications'
    template_name = 'topics.html'
    
class TopicDetailView(DetailView):
    template_name = 'topic.html'
    PER_PAGE = 20
    
    def get_object(self):
        obj = get_object_or_404(models.Topic, slug=self.kwargs['topic_slug'])
        return obj
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topic_posts = self.object.blog_posts.all()
        paginator = Paginator(topic_posts, 30)
        page = self.request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        ctx['posts'] = posts
        
        return ctx
    
class ProfileDetailView(DetailView):
    template_name = 'profile.html'
    PER_PAGE = 10
    
    def get_object(self):
        username = self.kwargs['username']
        user = get_object_or_404(get_user_model(), username=username)
        obj = get_object_or_404(models.Profile, user=user)
        return obj
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        posts_list = self.object.blog_posts.all()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(posts_list, self.PER_PAGE)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        ctx['posts'] = posts
        if self.request.user.is_authenticated:
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
        try:
            suggestions = models.BlogPost.objects.topic_suggestions(topic, 3).\
                exclude(id=self.object.id)
            ctx['topic_suggestions'] = suggestions
        except AttributeError:
            topics = models.Topic.objects.exclude(id=topic.id).all()
            topics = sample(list(topics), 3)
            ctx['topics'] = topics
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

@login_required
def thumbs(request, blog_post_slug, action):
    post = models.BlogPost.objects.get(slug=blog_post_slug)
    if action == 'UP':
        post.thumbs_up += 1
    elif action == 'DOWN':
        post.thumbs_down += 1
    post.save()
    return redirect(post.get_absolute_url())
    
class BlogPostCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.BlogPostForm
    template_name = 'blog_post_create.html'
    
    def dispatch(self, *args, **kwargs):
        if not self.request.user.profile.confirmed:
            messages.warning(self.request, 'confirm your email first before writing an article')
            return redirect('home')
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        form.instance.slug = slugify(form.instance.title)
        form.instance.active = True
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