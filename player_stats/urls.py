from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # This is for the homepage
    path('search/', views.search_player, name='search_player'),  # This handles player searches
    path('stats/', views.player_stats, name='player_stats'),  # This displays player stats
]
