from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
# from multiselectfield import MultiSelectField

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('имя тэга', max_length=255)
    value = models.CharField('значение тэга', max_length=50)
    color = models.CharField('цвет тэга в шаблоне', max_length=30, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'


class Ingredient(models.Model):
    title = models.CharField('ингредиент', max_length=50)
    dimention = models.CharField('единица измерения', max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'dimention'],
                name='unique_ingredient'
            ),
        ]
        ordering = ['title']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
    
    def __str__(self):
        return f'{self.title}, {self.dimention}'


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
        related_name='recipes',
        verbose_name='ингредиент',
    )
    tag = models.ManyToManyField(Tag, verbose_name='тэг')
    time = models.PositiveSmallIntegerField('время приготовления, мин.')
    slug = models.SlugField('путь', unique=True, editable=False)
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.title


class VolumeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, 
        verbose_name='ингредиент',
        on_delete=CASCADE,
        related_name='volume_ingredient'
    )
    quantity = models.PositiveIntegerField('количество')

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name} - {self.quantity} {self.ingredient.units}'


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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchase',
        verbose_name='рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_purchase'
            ),
        ]
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'