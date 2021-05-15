from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from recipes.utils import get_ingredients
from django.forms import CheckboxSelectMultiple, ModelForm, ClearableFileInput
 
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

    def save(self, commit=True):
        request = self.initial['request']
        recipe = super().save(commit=False)
        recipe.author = request.user
        recipe.save()
        self.save_m2m()
        ingredients = get_ingredients(request)
        for title, quantity in ingredients.items():
            ingredient = get_object_or_404(Ingredient, title=title)
            recipe_ing = VolumeIngredient(recipe=recipe,
                                          ingredient=ingredient,
                                          quantity=quantity)
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


    # def clean_ingredients(self):
    #     """Валидатор для ингредиентов."""
    #     ingredient_names = self.data.getlist('nameIngredient')
    #     ingredient_units = self.data.getlist('unitsIngredient')
    #     ingredient_amounts = self.data.getlist('valueIngredient')
    #     ingredients_clean = []
    #     for ingredient in zip(ingredient_names, ingredient_units,
    #                         ingredient_amounts):
    #         if not int(ingredient[2]) > 0:
    #             raise ValidationError('Количество ингредиентов должно '
    #                                         'быть положительным и не нулевым')
    #         elif not Ingredient.objects.filter(title=ingredient[0]).exists():
    #             raise ValidationError(
    #                 'Ингредиенты должны быть из списка')
    #         else:
    #             ingredients_clean.append({'title': ingredient[0],
    #                                     'dimension': ingredient[1],
    #                                     'quantity': ingredient[2]})
    #     if len(ingredients_clean) == 0:
    #         raise ValidationError('Добавьте ингредиент')
    #     return ingredients_clean

    # def clean_name(self):
    #     """Валидатор для названия рецептов."""
    #     data = self.cleaned_data['title']
    #     if len(data) == 0:
    #         raise ValidationError('Добавьте название рецепта')
    #     return data

    # def clean_description(self):
    #     """Валидатор для описания рецептов рецептов."""
    #     data = self.cleaned_data['description']
    #     if len(data) == 0:
    #         raise ValidationError('Добавьте описание рецепта')
    #     return data

    # def clean_tags(self):
    #     """Валидатор для описания рецептов рецептов."""
    #     data = self.cleaned_data['tag']
    #     if len(data) == 0:
    #         raise ValidationError('Добавьте тег')
    #     return data