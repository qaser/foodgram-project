from django.forms import CheckboxSelectMultiple, ModelForm

from recipes.models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'image', 'tag', 'time', 'description')
        widgets = {'tag': CheckboxSelectMultiple()}
