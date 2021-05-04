from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Exists, OuterRef


MESSAGE_MIN_TIME = 'Время приготовления должно быть не меньше 1 минуты.'
MESSAGE_MIN_QUANTITY = 'Количество ингредиента должно быть не меньше 1'

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('имя тэга', max_length=255)
    value = models.CharField('слаг тэга', max_length=50)
    color = models.CharField('цвет тэга в шаблоне', max_length=30, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'


class Ingredient(models.Model):
    title = models.CharField('ингредиент', max_length=50)
    dimension = models.CharField('единица измерения', max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'dimension'],
                name='unique_ingredient'
            ),
        ]
        ordering = ['title']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.title}, {self.dimension}'


# class RecipeQuerySet(models.QuerySet):

#     def recipe_with_tag(self, tags):  # передаю теги из view
#         # tag = [tag for tag in tags]
#         return self.filter(
#             tag__value__in=tags
#         ).select_related('author').prefetch_related('tag').distinct()

#     def selective_annotation(self, bask=False, fav=False, subs=False, **kwargs):
#         if bask:
#             self = self.annotate(basket=Exists(Purchase.objects.filter(recipe=OuterRef('pk'), **kwargs)))
#         if fav:
#             self = self.annotate(favorite=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), **kwargs)))
#         if subs:
#             self = self.annotate(subscribe=Exists(Subscription.objects.filter(author=OuterRef('author'), **kwargs)))
#         return self


class RecipeManager(models.Manager):
    def user_favor(self, user):
        """Возвращает любимые рецепты пользователя"""
        favorite_recipes_ids = list(Favorite.objects.filter(
            user=user).values_list('recipe_id', flat=True))
        return self.get_queryset().filter(id__in=favorite_recipes_ids)

    def user_purchase(self, user):
        """Возвращает рецепты, добавленные в список покупок"""
        purchase_recipes_ids = list(Purchase.objects.filter(
            user=user).values_list('recipe_id', flat=True))
        return self.get_queryset().filter(id__in=purchase_recipes_ids)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='автор',
        related_name='recipes'
    )
    title = models.CharField('название рецепта', max_length=200)
    image = models.ImageField('изображение', upload_to='recipes/',)
    description = models.TextField(
        'описание рецепта',
        blank=False,
        null=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='VolumeIngredient',
        through_fields=('recipe', 'ingredient')
    )
    tag = models.ManyToManyField(Tag, verbose_name='тэг')
    time = models.PositiveSmallIntegerField(
        'время приготовления, мин.',
        validators=[MinValueValidator(1, message=MESSAGE_MIN_TIME)]
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )
    objects = RecipeManager()

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.title


class VolumeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='volume_ingredient')
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=CASCADE,
        related_name='volume_ingredient'
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(1, message=MESSAGE_MIN_QUANTITY)]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.title} - {self.quantity} {self.ingredient.dimension}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор рецепта',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def clean(self):
        if self.author == self.user:
            raise ValidationError(
                'Пользователь не может подписываться сам на себя'
            )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_purchase'
            ),
        ]
