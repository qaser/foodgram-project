from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Ingredient, VolumeIngredient, Recipe, User, Subscription
from .forms import RecipeForm


# function for split many recipes on pages
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


@cache_page(20, key_prefix='index_page')
def index(request):
    tag = request.GET.getlist('filters')
    recipes_list = Recipe.objects.all()
    if tag:
        recipe_list = recipes_list.filter(tag=tag).distinct().all()
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


def profile(request, username):
    user = get_object_or_404(User, username=username)
    recipe_author = user.recipes.all()
    selection = split_on_page(request, recipe_author)
    follow = None
    if request.user.is_authenticated:
        follow = Subscription.objects.filter(
            user=request.user,
            author=user).exists()
    return render(
        request,
        'recipes/authorRecipe.html',
        {**{'username': user, 'follow': follow}, **selection},
    )


@login_required
def follow_index(request):
    users_list = User.objects.filter(following__user=request.user)
    selection = split_on_page(request, users_list)
    # paginator = Paginator(recipes_list, 3)
    return render(request, 'recipes/myFollow.html', selection)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Subscription.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollow = Subscription.objects.get(user=request.user, author=author)
    unfollow.delete()
    return redirect('profile', username=username)


# @login_required
# def new_recipe(request):
#     form = RecipeForm(request.POST or None, files=request.FILES or None)
#     if form.is_valid():
#         form.instance.author = request.user
#         form.save()
#         return redirect('index')
#     return render(request, 'recipes/formRecipe.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import RecipeForm
from .models import (
    Recipe,
    Ingredient,
    User,
    Follow,
    ShoppingList,
    RecipeIngredients
)
from .utils import gen_shopping_list, get_ingredients


# Количество рецептов на странице
PAGES = 9


def index(request):
    tag = request.GET.getlist('filters')
    recipe_list = Recipe.objects.all()
    if tag:
        recipe_list = recipe_list.filter(tag__value__in=tag).distinct().all()
    paginator = Paginator(recipe_list, PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator, }
    )


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    tag = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(author=profile.pk).all()
    if tag:
        recipe_list = recipe_list.filter(tag__value__in=tag)
    paginator = Paginator(recipe_list, PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {
            'profile': profile,
            'recipe_list': recipe_list,
            'page': page,
            'paginator': paginator
        }
    )


@login_required
def new_recipe(request):
    user = User.objects.get(username=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingredients = get_ingredients(request)
        if not ingredients:
            form.add_error(None, 'Добавьте ингредиенты')
        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = user
            recipe.save()
            for ing_name, amount in ingredients.items():
                ingredient = get_object_or_404(Ingredient, title=ing_name)
                recipe_ing = RecipeIngredients(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
                recipe_ing.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'new_recipe.html', {'form': form})


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipe', recipe_id=recipe.id)
    if request.method == "POST":
        form = RecipeForm(
            request.POST or None,
            files=request.FILES or None,
            instance=recipe
        )
        ingredients = get_ingredients(request)
        if form.is_valid():
            RecipeIngredients.objects.filter(recipe=recipe).delete()
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            recipe.ingredients.all().delete()
            for ing_name, amount in ingredients.items():
                ingredient = get_object_or_404(Ingredient, title=ing_name)
                recipe_ing = RecipeIngredients(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
                recipe_ing.save()
            form.save_m2m()
            return redirect('index')
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe
    )
    return render(
        request,
        'change_recipe.html',
        {'form': form, 'recipe': recipe, }
    )


def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    profile = get_object_or_404(User, username=username)
    return render(
        request,
        'recipe.html',
        {'profile': profile, 'recipe': recipe, }
    )


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect('index')


@login_required
def follow(request, username):
    user = get_object_or_404(User, username=username)
    author_list = Follow.objects.filter(user=user).all()
    paginator = Paginator(author_list, PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator, 'authors': author_list}
    )


@login_required
def follow_recipe(request, username):
    tag = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(favor__user__id=request.user.id).all()
    if tag:
        recipe_list = recipe_list.filter(tag__value__in=tag).distinct()
    paginator = Paginator(recipe_list, PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'favorite.html',
        {'page': page, 'paginator': paginator, }
    )


def shopping_list(request):
    shopping_list = ShoppingList.objects.filter(user=request.user).all()
    return render(
        request,
        'shopping-list.html',
        {'shopping_list': shopping_list}
    )


@login_required
def download(request):
    result = gen_shopping_list(request)
    filename = 'ingredients.txt'
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = \
        'attachment; filename={0}'.format(filename)
    return response