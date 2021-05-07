from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Ingredient, VolumeIngredient, Recipe


class RecipeForm(forms.ModelForm):
    # prep_time = forms.IntegerField(
    #     min_value=1,
    #     required=True,
    # )

    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'time', 'description', 'image')

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.fields['tag'].error_messages = {
            'required': 'Выберите хотя бы один тег'}

    def clean_ingredient(self):
        super().clean()
        new_ingredients_list = {}
        for key, title in self.data.items():
            if 'nameIngredient_' in key:
                elem = key.split("_")
                new_ingredients_list[title] = int(self.data[f'valueIngredient'
                                                            f'_{elem[1]}'])
        ing_titles = self.data.getlist("nameIngredient")
        ing_amount = self.data.getlist("valueIngredient")
        for title, amount in new_ingredients_list.items():
            ing_titles.append(title)
            ing_amount.append(amount)
        clean_items = {}
        for number, item in enumerate(ing_titles):
            ingredient = get_object_or_404(Ingredients, title=item)
            clean_items[ingredient] = ing_amount[number]
        self.cleaned_data['items'] = clean_items
        return self.cleaned_data['items']

    def clean(self):
        ingredients = self.clean_ingredient()
        if len(ingredients) == 0:
            raise ValidationError(
                'Из ничего вкусно не получится! Добавьте что-нибудь',
            )
        for value in ingredients.values():
            if int(value) < 1:
                raise ValidationError(
                    'Уберите ингридиент с 0 значением',
                )

    def save(self, commit=True):
        request = self.initial["request"]
        recipe = super().save(commit=False)
        recipe.author = request.user
        recipe.save()
        self.save_m2m()
        new_ingredients = self.clean_ingridient()
        recipe_ingredients = VolumeIngredient.objects.filter(
            recipe=self.instance)
        recipe_ingredients.delete()
        for ingredient, quantity in new_ingredients.items():
            VolumeIngredient.objects.update_or_create(
                recipe=self.instance,
                ingredient=ingredient,
                quantity=quantity)
        return self.instance



# from django.core.exceptions import ValidationError
# from django.forms import CheckboxSelectMultiple, ModelForm

# from recipes.models import Recipe


# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ('title', 'image', 'tag', 'time', 'description')
#         widgets = {'tag': CheckboxSelectMultiple()}

# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ['title', 'tags', 'cooking_time', 'description', 'image']

# class RecipeForm(ModelForm):
#     class Meta:
#         model = Recipe
#         fields = ('title', 'tag', 'time', 'description', 'image',)

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