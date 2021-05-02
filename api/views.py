from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets, status
from django.http import JsonResponse


from recipes.models import Ingredient, Subscription, Favorite
from .serializers import (IngredientSerializer, SubscriptionSerializer,
                          FavoriteSerializer, PurchaseSerializer)


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    def get_object(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {
            self.lookup_field: self.kwargs[lookup_url_kwarg],
            **kwargs,
        }
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(user=self.request.user)
        if obj.delete():
            return JsonResponse({'Success': True}, status=status.HTTP_200_OK)
        return JsonResponse({'Success': False})


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^title',)


class SubscriptionViewSet(CreateDestroyViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = 'author'


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    lookup_field = 'recipe'


class PurchaseViewSet(mixins.ListModelMixin, CreateDestroyViewSet):
    serializer_class = PurchaseSerializer
    lookup_field = 'recipe'

    def get_queryset(self):
        return self.request.user.purchases.all()
