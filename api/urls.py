from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router.register(
    'subscriptions',
    views.SubscriptionViewSet,
    basename='subscriptions'
)
router.register('favorites', views.FavoriteViewSet, basename='favorites')
router.register('purchases', views.PurchaseViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
]
