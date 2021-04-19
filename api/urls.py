from django.urls import path
from . import views


urlpatterns = [
    path('ingredients', views.Ingredients.as_view(), name='ingredients'),
    path('favorites', views.Favorites.as_view(), name='favor_add'),
    path(
        'favorites/<int:recipe_id>',
        views.Favorites.as_view(),
        name='favor_remove'
    ),
    path('subscriptions', views.Subscriptions.as_view(), name='sub_add'),
    path(
        'subscriptions/<int:author_id>',
        views.Subscriptions.as_view(),
        name='sub_remove',
    ),
    path(
        'purchases',
        views.Purchases.as_view(),
        name='add_to_cart'
    ),
    path(
        'purchases/<int:recipe_id>',
        views.Purchases.as_view(),
        name='remove_from_cart'
    ),
]
