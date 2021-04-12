from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from django.core.validators import MinValueValidator

User = get_user_model()


class TagName(models.TextChoices):
    BREAKFAST = 'завтрак'
    SUPPER = 'обед'
    DINNER = 'ужин'


class Tag(models.Model):
    name = models.CharField(
        'имя тега',
        choices=TagName.choices,
        db_index=True,
        max_length=20

    )
    slug = models.SlugField(
        unique=True,
        verbose_name='путь',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=30)
    measure = models.CharField('единица измерения', max_length=10)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
    
    def __str__(self):
        return f'{self.name}, {self.measure}'


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
    ingredient = models.ManyToManyField(
        Ingredient,
        # related_name='recipes',
        verbose_name='ингредиент',
        through='RecipeIngredient'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        db_index=True,
        verbose_name='тег'
    )
    time = models.PositiveSmallIntegerField('время приготовления')
    slug = models.SlugField('путь', unique=True, max_length=20)
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


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, 
        verbose_name='ингредиент',
        on_delete=CASCADE
    )
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        verbose_name='количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'ингредиенты в рецепте'
