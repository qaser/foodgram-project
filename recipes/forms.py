from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import CheckboxSelectMultiple, ClearableFileInput, ModelForm

from recipes.models import Ingredient, Recipe, VolumeIngredient


class ImageWidget(ClearableFileInput):
    template_name = 'recipes/extend/form_extend/image_widget.html'


# из выявленных и оставшихся проблем:
# - нет проверки дублирования ингредиентов, сохраняется последний
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
        # здесь проверяю существует ли рецепт и тяну его ингредиенты из БД
        # а так же формирую из них словарь. структура данных:
        # 'название ингредиента': {'quantity': , 'dimension': , 'check': }
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
                self.ingredients[name] = {'quantity': data.get(value)}
                self.ingredients[name].update(
                    {'dimension': data.get(dimention)}
                )
                # здесь тоже все подряд ингредиенты помечаются единицей
                self.ingredients[name].update({'check': 1})

    def clean(self):
        bad_ings = []
        null_ings = []
        if not self.ingredients:
            raise ValidationError('Добавьте ингредиенты для Вашего рецепта')
        for title, dict_data in self.ingredients.items():
            # обработка ввода числа с точкой
            try:
                quantity = int(dict_data['quantity'])
            except ValueError:
                first_num, _, _ = dict_data['quantity'].partition('.')
                # подменяю число с точкой на норм число
                first_num = (0 if first_num == '' else first_num)
                self.ingredients[title].update({'quantity': first_num})
                quantity = int(first_num)
            if quantity < 1 and dict_data['dimension'] != 'по вкусу':
                # а вот здесь плохиши получают отметку "0"
                self.ingredients[title].update({'check': 0})
                null_ings.append(title)
            try:
                ingredient = Ingredient.objects.filter(title=title).get()
                # здесь в словарь закидываю ингредиенты
                self.ingredients[title].update({'ingredient': ingredient})
            except ObjectDoesNotExist:
                self.ingredients[title].update({'check': 0})
                bad_ings.append(title)
        if bad_ings:
            error_text_tail = ', '.join(bad_ings)
            self.add_error(
                None, ('Выбирайте из выпадающего списка. '
                       f'Этих ингредиентов нет в базе: {error_text_tail}')
            )
        if null_ings:
            # обработка неправильных ингредиентов да еще и с нулём
            very_bad_ings = list(set(bad_ings) & set(null_ings))
            uniq_ing = [i for i in null_ings if i not in very_bad_ings]
            error_tail = ', '.join(uniq_ing)
            if uniq_ing:
                self.add_error(
                    None,
                    f'Добавьте побольше следующих ингредиентов: {error_tail}'
                )
        return super().clean()

    def save(self, commit=True):
        recipe = super().save(commit=False)
        recipe.save()
        obj = [
            VolumeIngredient(
                recipe=recipe,
                ingredient=data.get('ingredient'),
                quantity=data.get('quantity')
            ) for data in self.ingredients.values()
        ]
        recipe.volume_ingredient.all().delete()
        VolumeIngredient.objects.bulk_create(obj)
        self.save_m2m()
        return recipe
