from django import forms

from .models import Ingredient, VolumeIngredient, Recipe, Tag
from .utils import get_ingredients


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )

    class Meta:
        model = Recipe
        fields = ('title', 'tags', 'ingredients',
                  'time', 'description', 'image')

    def clean_ingredients(self):
        ingredients = list(
            zip(
                self.data.getlist('nameIngredient'),
                self.data.getlist('unitsIngredient'),
                self.data.getlist('valueIngredient'),
            ),
        )
        if not ingredients:
            raise forms.ValidationError('Добавьте ингредиент')

        ingredients_clean = []
        for title, unit, amount in ingredients:
            if int(amount) < 0:
                raise forms.ValidationError(
                    'Добавьте хотя бы один ингредиент'
                )
            elif not Ingredient.objects.filter(title=title).exists():
                raise forms.ValidationError(
                    'Ингредиенты должны быть из списка')
            else:
                ingredients_clean.append({
                    'title': title,
                    'unit': unit,
                    'amount': amount,
                })
        return ingredients_clean

    def clean_title(self):
        data = self.cleaned_data['title']
        if not data:
            raise forms.ValidationError('Добавьте название рецепта')
        return data

    def clean_description(self):
        data = self.cleaned_data['description']
        if not data:
            raise forms.ValidationError('Добавьте описание рецепта')
        return data

    def clean_tags(self):
        data = self.cleaned_data['tags']
        if not data:
            raise forms.ValidationError('Добавьте тег')
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.initial['author']
        instance.save()
        ingredients = self.cleaned_data['ingredients']
        self.cleaned_data['ingredients'] = []
        self.save_m2m()
        VolumeIngredient.objects.bulk_create(
            get_ingredients(ingredients, instance))
        return instance



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