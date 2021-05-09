from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Ingredient, VolumeIngredient, Recipe, Tag
from .utils import get_ingredients


class RecipeForm(forms.ModelForm):
    # recipe_tag = forms.ModelMultipleChoiceField(
    #     queryset=Tag.objects.all(),
    # )

    class Meta:
        model = Recipe
        fields = ('title', 'tag', 'ingredients', 'time', 'description',
                  'image')
        # widgets = {
        #     "tags": forms.CheckboxSelectMultiple(),
        # }
        # help_texts = {
        #     'title': 'Введите название рецепта.',
        #     'description': 'Введите описание рецепта',
        #     'image': 'Выберите изображение для рецепта',
        #     'time': 'Введите время приготовления блюда',
        # }


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
                self.ingredients[name] = {'amount': int(data.get(value))}

    def save(self, commit=True):
        recipe = super().save(commit=False)
        recipe.save()
        objects = []
        for data in self.ingredients.values():
            objects.append(VolumeIngredient(recipe=recipe,
                                            ingredient=data.get('object'),
                                            quantity=data.get('amount'), )
                           )
        if objects:
            recipe.amount.all().delete()
            VolumeIngredient.objects.bulk_create(objects)
        self.save_m2m()
        return recipe

    def clean(self):
        if not self.ingredients:
            raise forms.ValidationError('Empty ingredients list not allowed')
        for title, amount in self.ingredients.items():
            if amount.get('amount') < 0:
                raise forms.ValidationError(f'Invalid value for {title}')
            try:
                ingredient = Ingredient.objects.filter(title=title).get()
                self.ingredients[title].update({'object': ingredient})
            except ObjectDoesNotExist:
                raise forms.ValidationError(f'{title} not valid ingredient')
        return super().clean()


    # def clean(self):
    #     super().clean()
    #     if (
    #         len(self.data.getlist('nameIngredient')) !=
    #         len(set(self.data.getlist('nameIngredient')))
    #     ):
    #         raise forms.ValidationError(
    #             'Пожалуйста, уберите повторяющиеся ингредиенты'
    #         )
    #     if 'nameIngredient' not in self.data:
    #         raise forms.ValidationError(
    #             'Нужно добавить минимум один ингридиент'
    #         )
    #     if any(
    #         map(lambda x: int(x) < 0, self.data.getlist('valueIngredient'))
    #     ):
    #         raise forms.ValidationError(
    #             'Количество ингредиента не может быть отрицательным'
    #         )

    # def clean_ingredients(self):
    #     print(self.data)
    #     ingredients = list(
    #         zip(
    #             self.data.getlist('nameIngredient'),
    #             self.data.getlist('unitsIngredient'),
    #             self.data.getlist('valueIngredient'),
    #         ),
    #     )
    #     if not ingredients:
    #         raise forms.ValidationError('Добавьте ингредиент')
    #     ingredients_clean = []
    #     for title, dimension, quantity in ingredients:
    #         if int(quantity) < 0:
    #             raise forms.ValidationError(
    #                 'Количество ингредиентов должно быть больше нуля'
    #             )
    #         elif not Ingredient.objects.filter(title=title).exists():
    #             raise forms.ValidationError(
    #                 'Ингредиенты должны быть из списка')
    #         else:
    #             ingredients_clean.append({
    #                 'title': title,
    #                 'dimention': dimension,
    #                 'quantity': quantity,
    #             })
    #     return ingredients_clean

    # def clean_title(self):
    #     data = self.cleaned_data['title']
    #     if not data:
    #         raise forms.ValidationError('Добавьте название рецепта')
    #     return data

    # def clean_description(self):
    #     data = self.cleaned_data['description']
    #     if not data:
    #         raise forms.ValidationError('Добавьте описание рецепта')
    #     return data

    # def clean_tags(self):
    #     data = self.cleaned_data['tags']
    #     if not data:
    #         raise forms.ValidationError('Добавьте тег')
    #     return data

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
