from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Ingredient, RecipeIngredient, Recipe


# function for split many posts on pages
def split_on_page(request, post_page):
    paginator = Paginator(post_page, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


@cache_page(20, key_prefix='index_page')
def index(request):
    recipes_list = Recipe.objects.all()
    selection = split_on_page(request, recipes_list)
    return render(request, 'recipes/index.html', selection)


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredient_in_recipe.all()
    return render(
        request,
        'recipes/single_recipe.html',
        {'recipe': recipe, 'ingredients': ingredients},
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)