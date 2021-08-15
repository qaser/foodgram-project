from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Favorite, Ingredient, Purchase, Subscription


class CustomModelSerializer(serializers.ModelSerializer):
    def create(self, data):
        data['user'] = self.context['request'].user
        return self.Meta.model.objects.create(**data)


class FavoriteSerializer(CustomModelSerializer):
    class Meta:
        fields = ('recipe', )
        model = Favorite


class PurchaseSerializer(CustomModelSerializer):
    class Meta:
        fields = ('recipe', )
        model = Purchase


class SubscriptionSerializer(CustomModelSerializer):
    class Meta:
        fields = ('author', )
        model = Subscription

    def validate_author(self, value):
        user = self.context['request'].user
        if user.id == value:
            raise ValidationError('Нельзя подписаться на себя')
        return value


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'dimension')
        model = Ingredient
