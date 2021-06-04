from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import CheckboxSelectMultiple, ClearableFileInput, ModelForm

from recipes.models import Ingredient, Recipe, VolumeIngredient


class ImageWidget(ClearableFileInput):
    template_name = 'recipes/extend/form_extend/image_widget.html'

# долго вымучивал возможность сохранять годные ингредиенты и 
# избавляться от плохих. Возможно код немного попахивает.
# sad but true...
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
        # здесь проверяю есть ли в БД рецепт и тяну его ингредиенты
        # а так же формирую из них словарь
        # структура данных:
        # 'название ингредиента': {'quantity': , 'dimension': , 'check': }
        # в шаблоне ingredients.html не очень красиво: использую индексы
        elif 'instance' in kwargs:
            for i in kwargs['instance'].volume_ingredient.all():
                # для индентификации годных ингредиентов делаю пометку "check"
                # изначально она для всех равна 1
                self.ingredients[i.ingredient.title] = {'check': 1}
                self.ingredients[i.ingredient.title].update(
                    {'quantity': int(i.quantity)}
                )
                self.ingredients[i.ingredient.title].update(
                    {'dimension': i.ingredient.dimension}
                )
        super().__init__(data=data, *args, **kwargs)

    def get_ingredients(self, data):
        for key, name in data.items():
            if key.startswith('nameIngredient'):
                _, _, number = key.partition('_')
                value = f'valueIngredient_{number}'
                dimention = f'unitsIngredient_{number}'
                self.ingredients[name] = {'quantity': int(data.get(value))}
                self.ingredients[name].update(
                    {'dimension': data.get(dimention)}
                )
                # здесь тоже все подряд ингредиенты помечаются единицей
                self.ingredients[name].update({'check': 1})

    def clean(self):
        bad_ingredients = []
        null_ingredients = []
        if not self.ingredients:
            raise ValidationError('Добавьте ингредиенты для Вашего рецепта')
        for title, dict_data in self.ingredients.items():
            if dict_data['quantity'] < 1:
                # а вот здесь плохиши получают отметку "0"
                # и выбывают из игры
                self.ingredients[title].update({'check': 0})
                null_ingredients.append(title)
            try:
                ingredient = Ingredient.objects.filter(title=title).get()
                # здесь в словарь закидываю ингредиенты, скоро в БД буду лить
                self.ingredients[title].update({'ingredient': ingredient})
            except ObjectDoesNotExist:
                # и здесь плохие ингредиенты получают метку "0"
                self.ingredients[title].update({'check': 0})
                bad_ingredients.append(title)
        if bad_ingredients:
            error_text_tail = ', '.join(bad_ingredients)
            self.add_error(
                None, f'Этих ингредиентов нет в базе: {error_text_tail}'
            )
        if null_ingredients:
            # понесло меня: если вдруг пользователь внёс неправильные
            # ингредиенты да еще и с нулём, то у него нет шансов
            very_bad_ingredients = list(
                set(bad_ingredients) & set(null_ingredients)
            )
            # больше списков богу списков!
            x = [i for i in null_ingredients if i not in very_bad_ingredients]
            error_text_tail = ', '.join(x)
            if x:
                self.add_error(
                    None,
                    ('Добавьте побольше следующих '
                    f'ингредиентов: {error_text_tail}'))
        return super().clean()

    def save(self, commit=True):
        recipe = super().save(commit=False)
        recipe.save()
        # вот здесь формируются данные для БД
        obj = [
            VolumeIngredient(
                recipe=recipe,
                ingredient=data.get('ingredient'),
                quantity=data.get('quantity')
            ) for data in self.ingredients.values()
        ]
        if obj:
            recipe.volume_ingredient.all().delete()
            VolumeIngredient.objects.bulk_create(obj)
        self.save_m2m()
        return recipe
