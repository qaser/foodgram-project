from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.deletion import CASCADE

MESSAGE_MIN_TIME = 'Время приготовления должно быть не меньше 1 минуты.'
MESSAGE_MIN_QUANTITY = 'Количество ингредиента должно быть не меньше 1'

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('имя тэга', max_length=255)
    value = models.CharField('слаг тэга', max_length=50)
    color = models.CharField('цвет тэга в шаблоне', max_length=30, null=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    title = models.CharField('ингредиент', max_length=500)
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


class RecipeQuerySet(models.QuerySet):
    # отдельная выборка через теги
    def get_by_tags(self, tag, user):
        return (
            self.filter(tag__value__in=tag).distinct().is_annotated(user=user)
            if tag
            else self.is_annotated(user=user)
        )

    # отдельная выборка для избранного
    def user_favor(self, user):
        favorite_recipes = list(
            user.favorites.all().values_list('recipe_id', flat=True)
        )
        return self.filter(id__in=favorite_recipes)

    # отдельная выборка для заказов
    def user_purchase(self, user):
        purchase_recipes = list(
            user.purchases.all().values_list('recipe_id', flat=True)
        )
        return self.filter(id__in=purchase_recipes)

    def is_annotated(self, user):
        if user.is_authenticated:
            in_purchases = Purchase.objects.filter(
                recipe=models.OuterRef('id'),
                user=user
            )
            in_favor = Favorite.objects.filter(
                recipe=models.OuterRef('id'),
                user=user
            )
            in_subs = Subscription.objects.filter(
                author=models.OuterRef('author'),
                user=user
            )
            # возврат queryset'a
            return self.annotate(
                favorite=models.Exists(in_favor),  # рецепт в избранном
                purchased=models.Exists(in_purchases),  # вхождение в заказ
                subs=models.Exists(in_subs)  # вхождение в подписку
            )
        return self


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
    objects = RecipeQuerySet.as_manager()

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
        return (f'{self.ingredient.title} - {self.quantity} '
                f'{self.ingredient.dimension}')


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
            # запрет подписки на уровне БД
            models.CheckConstraint(
                name='self_subscription_denied',
                check=~models.Q(user=models.F('author')),
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
