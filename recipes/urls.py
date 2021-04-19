from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('subscription/<str:username>', views.follow_index, name='follow'),
    # path('new-recipe/', views.new_recipe, name='new_recipe'),
    path('users/<str:username>/', views.profile, name='profile'),
    path('recipes/<int:recipe_id>/', views.recipe_view, name='recipe_view'),
    # path('recipes/<int:recipe_id>/edit/', views.post_edit, name='recipe_edit'),
    # path('recipes/<int:recipe_id>/delete/', views.post_delete, name='recipe_delete'),
    # path('favorite-recipe/<username>/', views.favor_recipe, name='favorite-recipe'),
    # path('purchase/', views.shopping_list, name='purchase'),
    # path('save-purchase', views.download, name='save-purchase'),
]
