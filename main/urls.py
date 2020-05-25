from django.urls import path
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('<slug:blog_post_slug>/thumbs/<str:action>/', views.thumbs, name='thumbs'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('add/', views.BlogPostCreateView.as_view(), name='blog_post_create'),
    path('@<str:username>/follow/', views.follow_profile, name='follow_profile'),
    path('@<str:username>/unfollow/', views.unfollow_profile, name='unfollow_profile'),
    path('topic/<slug:topic_slug>/unfollow/', views.unfollow_topic, name='unfollow_topic'),
    path('topic/<slug:topic_slug>/follow/', views.follow_topic, name='follow_topic'),
    path('@<str:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('@<str:username>/<slug:blog_post_slug>', views.BlogPostDetailView.as_view(), name='blog_post'),
    path('topic/<slug:topic_slug>/', views.TopicDetailView.as_view(), name='topic'),
    path('topics/', views.TopicsListView.as_view(), name='topics'),
    path('', views.HomePageView.as_view(), name='home'),
]