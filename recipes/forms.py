from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import CheckboxSelectMultiple, ClearableFileInput, ModelForm

from recipes.models import Ingredient, Recipe, VolumeIngredient


class ImageWidget(ClearableFileInput):
    template_name = 'recipes/extend/image_widget.html'


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'image', 'tag', 'time', 'description')
        widgets = {
            'tag': CheckboxSelectMultiple(),
            'image': ImageWidget(),
        }

    def __init__(self, data=None, *args, **kwargs):
        self.ingredients = {}
        if data is not None:
            data = data.copy()
            self.get_ingredients(data)
        super().__init__(data=data, *args, **kwargs)

    def get_ingredients(self, data):
        for key, name in data.items():
            if key.startswith('nameIngredient'):
                _, _, number = key.partition('_')
                value = f'valueIngredient_{number}'
                self.ingredients[name] = {'quantity': int(data.get(value))}

    def save(self, commit=True):
        recipe = super().save(commit=False)
        recipe.save()
        objects = []
        for data in self.ingredients.values():
            objects.append(
                VolumeIngredient(
                    recipe=recipe,
                    ingredient=data.get('ingredient'),
                    quantity=data.get('quantity')
                )
            )
        if objects:
            recipe.volume_ingredient.all().delete()
            VolumeIngredient.objects.bulk_create(objects)
        self.save_m2m()
        return recipe

    def clean(self):
        if not self.ingredients:
            raise ValidationError('Добавьте ингредиенты для Вашего рецепта')
        for title, quantity in self.ingredients.items():
            if quantity['quantity'] < 1:
                raise ValidationError(
                    f'Количество ингредиента "{title}" '
                    'должно быть больше нуля.'
                )
            try:
                ingredient = Ingredient.objects.filter(title=title).get()
                self.ingredients[title].update({'ingredient': ingredient})
            except ObjectDoesNotExist:
                raise ValidationError('Выберите ингредиент из списка')
        return super().clean()
