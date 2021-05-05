from django.core.exceptions import ValidationError
from django.forms import CheckboxSelectMultiple, ModelForm

from recipes.models import Recipe


# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ('title', 'image', 'tag', 'time', 'description')
#         widgets = {'tag': CheckboxSelectMultiple()}

# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ['title', 'tags', 'cooking_time', 'description', 'image']

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'time', 'description', 'image',)

    # def clean(self):
    #     known_ids = []
    #     for items in self.data.keys():
    #         if 'nameIngredient' in items:
    #             name, id = items.split('_')
    #             known_ids.append(id)

    #     for id in known_ids:
    #         value = self.data.get(f'valueIngredient_{id}')

    #         if int(value) <= 0:
    #             raise ValidationError('Ингредиентов должно быть больше 0')