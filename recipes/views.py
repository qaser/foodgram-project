from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from foodgram.settings import PAGINATOR_PAGES
from django.views.generic import DetailView, ListView
from django.urls import reverse, reverse_lazy
from django.db.models import Count, Prefetch, Subquery, Sum


from .forms import RecipeForm
from .models import (Ingredient, Purchase, Recipe, Subscription, User,
                     VolumeIngredient, Favorite)
from .utils import get_ingredients, paginator_initial, get_recipes_by_tags


# function for split many recipes on pages
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    output = ''
    for arg in request.META['active_tags']:
        output = f'{output}&filters={arg}'
    url = reverse(request.resolver_match.url_name)
    if page_number is not None:
        if int(page_number) > paginator.num_pages:
            return redirect(f'{url}?page={paginator.num_pages}{output}')
    return {'page': page, 'paginator': paginator}


def page_out_of_paginator(request, limit_page):
    page_number = request.GET.get('page')
    url_tail = ''
    for tag in request.META['active_tags']:
        url_tail = f'{url_tail}&filters={tag}'
    url = reverse(request.resolver_match.url_name)
    if page_number is not None and int(page_number) > limit_page:
        # if int(page_number) > limit_page:
        return True
    return False


@cache_page(20, key_prefix='index_page')
def index(request):
    """Предоставляет список рецептов для всех пользователей"""
    recipe_list = Recipe.objects.all()
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    selection = split_on_page(request, recipes_by_tags.get('recipes'))
    paginator = Paginator(recipes_by_tags.get('recipes'), PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, **recipes_by_tags}
    output = ''
    for arg in request.META['active_tags']:
        output = f'{output}&filters={arg}'
    url = reverse(request.resolver_match.url_name)
    if page_number is not None and int(page_number) > paginator.num_pages:
        return redirect(f'{url}?page={paginator.num_pages}{output}')
    context = {**recipes_by_tags, **selection}
    return render(request, 'recipes/index.html', context)


def profile(request, username):
    """Показывает страницу автора рецепта"""
    # user = request.user
    user = get_object_or_404(User, username=username)
    recipe_list = user.recipes.order_by('-pub_date')
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    paginator = Paginator(recipes_by_tags.get('recipes'), PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page': page,
        'paginator': paginator,
        **recipes_by_tags
    }
    return render(request, 'recipes/authorRecipe.html', context)


@login_required
def subscription_index(request, username):
    """Предоставляет список подписок пользователя"""
    subscriptions = Subscription.objects.filter(user=request.user)
    paginator = Paginator(subscriptions, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'subscriptions': subscriptions,
    }
    return render(request, 'recipes/myFollow.html', context)


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(
        request,
        'recipes/single_recipe.html',
        {'recipe': recipe},
    )


@login_required
def recipe_new(request):
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
                recipe_ing = VolumeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=amount
                )
                recipe_ing.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'recipes/formRecipe.html', {'form': form})


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
            # VolumeIngredient.objects.filter(recipe=recipe).delete()
            recipe.volume_ingredient.all().delete()
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            recipe.ingredients.all().delete()
            for ing_name, quantity in ingredients.items():
                ingredient = get_object_or_404(Ingredient, title=ing_name)
                recipe_ing = VolumeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=quantity
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
        'recipes/formChangeRecipe.html',
        {'form': form, 'recipe': recipe, }
    )


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect('index')


@login_required
def recipe_favor(request, username):
    """Предоставляет список любимых рецептов пользователя"""
    favorites_list = Recipe.objects.user_favor(user=request.user)
    favorites_by_tags = get_recipes_by_tags(request, favorites_list)
    paginator = Paginator(favorites_by_tags.get('recipes'), PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, **favorites_by_tags}
    return render(request, 'recipes/favorite.html', context)


def purchase_cart(request):
    purchase = Recipe.objects.user_purchase(user=request.user)
    return render(
        request,
        'recipes/shopList.html',
        {'purchase': purchase}
    )


@login_required
def purchase_save(request):
    title = 'recipe__ingredients__title'
    dimension = 'recipe__ingredients__dimension'
    quantity = 'recipe__volume_ingredient__quantity'

    ingredients = request.user.purchases.select_related('recipe').order_by(
        title).values(title, dimension).annotate(amount=Sum(quantity)).all()

    if not ingredients:
        return render(request, '/misc/400.html', status=400)

    text = 'Список покупок:\n\n'
    for number, ingredient in enumerate(ingredients, start=1):
        amount = ingredient['amount']
        text += (
            f'{number}) '
            f'{ingredient[title]}, '
            f'{ingredient[dimension]} - '
            f'{amount}\n'
        )
    response = HttpResponse(text, content_type='text/plain')
    filename = 'purchases.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
