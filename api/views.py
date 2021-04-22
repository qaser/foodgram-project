from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (FavoriteSerializer, PurchaseSerializer,
                             SubscriptionSerializer)
from recipes.models import Favorite, Purchase, Subscription, User


class CreateDestroyView(generics.CreateAPIView, generics.DestroyAPIView):
    api_name = ''

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user)
        if self.api_name == 'favorite':
            obj = user.favorites.filter(recipe__id=kwargs['id'])
        elif self.api_name == 'subscription':
            obj = user.follower.filter(author__id=kwargs['id'])
        else:
            obj = user.purchase.filter(recipe__id=kwargs['id'])
        if obj.delete():
            return Response({'Success': True})
        return Response({'Success': False})


class FavoritesView(CreateDestroyView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    api_name = 'favorite'


class SubscriptionView(CreateDestroyView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    api_name = 'subscription'


class PurchaseView(CreateDestroyView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    api_name = 'purchase'
