from django.forms import CheckboxSelectMultiple, ModelForm, ClearableFileInput
 
from recipes.models import Recipe 
 
 
class ImageFieldWidget(ClearableFileInput):
    template_name = 'recipes/extend/image_widget.html'


class RecipeForm(ModelForm): 
    class Meta: 
        model = Recipe 
        fields = ('title', 'image', 'tag', 'time', 'description') 
        widgets = {
            'tag': CheckboxSelectMultiple(),
            'image': ImageFieldWidget(),
        }