from django.contrib import admin
from django.urls import path
from player_stats import views

urlpatterns = [
    path('', views.home, name='home'),  # This is the root URL path for the home page
    path('stats/', views.player_stats, name='player_stats'),
    path('search/', views.search_player, name='search_player'),
]
