from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'subscriptions/',
        views.subscription_index,
        name='subscriptions'
    ),
    path('users/<str:username>/', views.profile, name='profile'),
    path('recipes/new/', views.recipe_new, name='recipe_new'),
    path('recipes/<int:recipe_id>/', views.recipe_view, name='recipe_view'),
    path(
        'recipes/<int:recipe_id>/edit/',
        views.recipe_edit,
        name='recipe_edit'
    ),
    path(
        'recipes/<int:recipe_id>/delete/',
        views.recipe_delete,
        name='recipe_delete'
    ),
    path(
        'recipes/favorite/',
        views.recipe_favor,
        name='recipe_favor'
    ),
    path('purchase/', views.purchase_cart, name='purchase'),
    path('save-purchase/', views.purchase_save, name='purchase_save'),
]
