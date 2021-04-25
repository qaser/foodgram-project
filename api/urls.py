from django.urls import path

from . import views

urlpatterns = [
    path(
        'favorites/',
        views.FavoritesView.as_view(),
        name='favor_add'
    ),
    path(
        'favorites/<int:id>/',
        views.FavoritesView.as_view(),
        name='favor_delete'
    ),
    path(
        'subscriptions/',
        views.SubscriptionView.as_view(),
        name='sub_add'
    ),
    path(
        'subscriptions/<str:id>/',
        views.SubscriptionView.as_view(),
        name='sub_delete'
    ),
    path(
        'purchases/',
        views.PurchaseView.as_view(),
        name='purchases_add'
    ),
    path(
        'purchases/<int:id>/',
        views.PurchaseView.as_view(),
        name='purchases_delete'
    ),
    path(
        'ingredients/',
        views.Ingredients.as_view(),
        name='get_ingredients'
    ),
]
