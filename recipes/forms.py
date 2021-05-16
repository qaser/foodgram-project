from django.core.exceptions import ValidationError
from django.forms import CheckboxSelectMultiple, ClearableFileInput, ModelForm
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, VolumeIngredient
from recipes.utils import get_ingredients


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

    def save(self, commit=True):
        request = self.initial['request']
        recipe = super().save(commit=False)
        recipe.author = request.user
        recipe.save()
        self.save_m2m()
        ingredients = get_ingredients(request)
        for title, quantity in ingredients.items():
            ingredient = get_object_or_404(Ingredient, title=title)
            recipe_ing = VolumeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity
            )
            recipe_ing.save()

    def clean(self):
        check_id = []
        for items in self.data.keys():
            if 'nameIngredient' in items:
                name, id = items.split('_')
                check_id.append(id)
        for id in check_id:
            value = self.data.get(f'valueIngredient_{id}')
            if float(value) <= 0:
                raise ValidationError('Добавьте хотя бы один ингредиент')
