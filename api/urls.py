from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'subscriptions',
    views.SubscriptionViewSet,
    basename='subscriptions'
)
router.register(r'favorites', views.FavoriteViewSet, basename='favorites')
router.register(r'purchases', views.PurchaseViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
]
