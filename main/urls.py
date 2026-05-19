from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('projects/', views.projects_list, name='projects_list'),
    path('support/', views.support_measures_list, name='support_measures'),
]
