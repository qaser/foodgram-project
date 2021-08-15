from django.urls import path

from . import views

app_name = 'service'

urlpatterns = [
    path('author/', views.AuthorView.as_view(), name='author'),
    path('tech/', views.TechView.as_view(), name='tech'),
]
