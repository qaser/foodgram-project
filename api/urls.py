from django.urls import include, path

from . import views
from rest_framework.routers import DefaultRouter


# from .views import (IngredientViewSet, SubscriptionViewSet, FavoriteViewSet,
#                     PurchaseViewSet)

router = DefaultRouter()
router.register(r'ingredients', views.IngredientViewSet, basename='ingredients')
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')
router.register(r'favorites', views.FavoriteViewSet, basename='favorites')
router.register(r'purchases', views.PurchaseViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns = [
#     path(
#         'favorites/',
#         views.FavoritesView.as_view(),
#         name='favor_add'
#     ),
#     path(
#         'favorites/<int:id>/',
#         views.FavoritesView.as_view(),
#         name='favor_delete'
#     ),
#     path(
#         'subscriptions/',
#         views.SubscriptionView.as_view(),
#         name='sub_add'
#     ),
#     path(
#         'subscriptions/<str:id>/',
#         views.SubscriptionView.as_view(),
#         name='sub_delete'
#     ),
#     path(
#         'purchases/',
#         views.PurchaseView.as_view(),
#         name='purchases_add'
#     ),
#     path(
#         'purchases/<int:id>/',
#         views.PurchaseView.as_view(),
#         name='purchases_delete'
#     ),
#     path(
#         'ingredients/',
#         views.Ingredients.as_view(),
#         name='get_ingredients'
#     ),
# ]
