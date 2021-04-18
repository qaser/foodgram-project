from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('follow/', views.follow_index, name='follow'),
#     path('group/<slug:slug>/', views.group_posts, name='group_name'),
#     path('new/', views.new_post, name='new_post'),
    path('users/<str:username>/', views.profile, name='profile'),
    path('recipes/<int:recipe_id>/', views.recipe_view, name='recipe'),
#     path('<str:username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
#     path('<username>/<int:post_id>/comment', views.add_comment, name='add_comment'),
    path('<str:username>/follow/', views.profile_follow, name='profile_follow'),
    path('<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
]
