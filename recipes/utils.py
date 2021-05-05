from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Tag

User = get_user_model()


def get_recipes_by_tags(request, recipes):
    """Возвращает набор рецептов в зависимости от выбранных тегов"""
    filters = ''
    active_tags = request.META['active_tags']
    for tag in active_tags:
        filters += f'&filters={tag}'
    if active_tags:
        recipes = recipes.filter(tag__value__in=active_tags).distinct().is_annotated(user=request.user)
        print(recipes)
    recipes = recipes.is_annotated(user=request.user)
    context = {'recipes': recipes, 'filters': filters}
    return context


def get_ingredients(request):
    ingredients = {}
    for key, title in request.POST.items():
        if not key.startswith('nameIngredient_'):
            continue
        arg = key.split('_')[1]
        amount = request.POST['valueIngredient_' + arg]
        ingredients[title] = amount
    return ingredients


def paginator_initial(request, model_objs, paginator_count):
    paginator = Paginator(model_objs, paginator_count)
    page_number = request.GET.get('page')
    if page_number:
        if not page_number.isdigit():
            page = paginator.get_page(None)
        elif int(page_number) > paginator.num_pages:
            page = paginator.get_page(paginator.num_pages)
        else:
            page = paginator.get_page(page_number)
        return paginator, page, page.object_list, page.has_other_pages()
    page = paginator.get_page(None)
    return paginator, page, page.object_list, page.has_other_pages()
