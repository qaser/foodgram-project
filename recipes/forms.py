from django.forms import ModelForm, CheckboxSelectMultiple

from recipe.models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'image', 'tag', 'time', 'description')
        widgets = {'tag': CheckboxSelectMultiple()}