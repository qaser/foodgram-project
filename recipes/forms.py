from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import CheckboxSelectMultiple, ClearableFileInput, ModelForm
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, VolumeIngredient
# from recipes.utils import get_ingredients


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
                self.ingredients[name] = {'volume': int(data.get(value))}

    def save(self, commit=True):
        # request = self.initial['request']
        recipe = super().save(commit=False)
        # recipe.author = request.user
        recipe.save()
        objects = []
        for data in self.ingredients.values():
            objects.append(VolumeIngredient(recipe=recipe,
                                            ingredient=data.get('object'),
                                            volume=data.get('volume'), )
                           )
        if objects:
            recipe.volume_ingredient.all().delete()
            VolumeIngredient.objects.bulk_create(objects)
        self.save_m2m()

    def clean(self):
        if not self.ingredients:
            raise ValidationError('Empty ingredients list not allowed')
        for title, volume in self.ingredients.items():
            if volume.get('volume') < 0:
                raise ValidationError(f'Invalid value for {title}')
            try:
                ingredient = Ingredient.objects.filter(title=title).get()
                self.ingredients[title].update({'object': ingredient})
            except ObjectDoesNotExist:
                raise ValidationError(f'{title} not valid ingredient')
        return super().clean()