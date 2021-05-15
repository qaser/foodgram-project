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


class RecipeManager(models.Manager):
    def get_queryset(self):
        return RecipeQuerySet(self.model, using=self._db)

    # проверка наличия аттрибутов у пользователя
    def is_annotated(self, user):
        return self.get_queryset().is_annotated(user=user)

    def user_favor(self, user):
        # любимые рецепты пользователя
        favorite_recipes = list(Favorite.objects.filter(
            user=user).values_list('recipe_id', flat=True))
        return self.get_queryset().filter(id__in=favorite_recipes)

    def user_purchase(self, user):
        # рецепты в корзине
        purchase_recipes = list(Purchase.objects.filter(
            user=user).values_list('recipe_id', flat=True))
        return self.get_queryset().filter(id__in=purchase_recipes)


class RecipeQuerySet(models.QuerySet):
    def is_annotated(self, user):
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
        return self.annotate(
            in_favored=models.Exists(in_favor),
            in_purchased=models.Exists(in_purchases),
            in_subscriptions=models.Exists(in_subs)
        )


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
            # запрет подписки на уровне БД
            models.CheckConstraint(
                name='self_subscription_denied',
                check=~models.Q(user__exact=models.F('author')),
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
