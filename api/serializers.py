from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from recipes.models import Ingredient, Subscription, Favorite, Purchase


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



# class FavoriteSerializer(serializers.ModelSerializer):
#     id = serializers.SlugRelatedField(
#         source='recipe',
#         slug_field='id',
#         queryset=Recipe.recipes.all()
#     )
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         fields = ['id', 'user']
#         model = Favorite


# class PurchaseSerializer(serializers.ModelSerializer):
#     id = serializers.SlugRelatedField(
#         source='recipe',
#         slug_field='id',
#         queryset=Recipe.recipes.all()
#     )
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         fields = ['id', 'user']
#         model = Purchase


# class SubscriptionSerializer(serializers.ModelSerializer):
#     id = serializers.SlugRelatedField(
#         source='author',
#         slug_field='id',
#         queryset=User.objects.all()
#     )
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         fields = ['id', 'user']
#         model = Subscription

#     def validate(self, attrs):
#         user = self.context['request'].user
#         if user == attrs:
#             raise serializers.ValidationError('Нельзя подписаться на себя')
#         return super().validate(attrs)