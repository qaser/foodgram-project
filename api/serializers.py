from rest_framework import serializers

from recipes.models import Favorite, Purchase, Recipe, Subscription, User


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='recipe',
        slug_field='id',
        queryset=Recipe.objects.all()
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ['id', 'user']
        model = Favorite


class PurchaseSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='recipe',
        slug_field='id',
        queryset=Recipe.objects.all()
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ['id', 'user']
        model = Purchase


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='author',
        slug_field='id',
        queryset=User.objects.all()
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ['id', 'user']
        model = Subscription

    def validate(self, attrs):
        if attrs['author'] == attrs['user']:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        return super().validate(attrs)
