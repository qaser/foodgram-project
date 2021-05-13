from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import RecipeForm
from .models import Ingredient, Recipe, Subscription, User, VolumeIngredient
from .utils import (generate_path, get_ingredients, get_ingredients_qwerty, get_recipes_by_tags,
                    page_out_of_paginator, save_recipe, split_on_page)


# список рецептов для главной страницы
@cache_page(20, key_prefix='index_page')
def index(request):
    recipe_list = Recipe.objects.all()
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    # выборка, разделённая на страницы
    selection = split_on_page(request, recipes_by_tags.get('recipes'))
    limit_page = selection['paginator'].num_pages
    check_paginator = page_out_of_paginator(request, limit_page)
    if check_paginator:
        redirect_path = generate_path(request, limit_page)
        return redirect(redirect_path)
    context = {'filters': recipes_by_tags['filters'], **selection}
    return render(request, 'recipes/index.html', context)


# страница автора рецептов
def profile(request, username):
    user = get_object_or_404(User, username=username)
    recipe_list = user.recipes.order_by('-pub_date')
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    selection = split_on_page(request, recipes_by_tags.get('recipes'))
    limit_page = selection['paginator'].num_pages
    check_paginator = page_out_of_paginator(request, limit_page)
    if check_paginator:
        redirect_path = generate_path(request, limit_page)
        return redirect(redirect_path)
    context = {'profile': user, **selection}
    return render(request, 'recipes/authorRecipe.html', context)


# список подписок пользователя
@login_required
def subscription_index(request, username):
    subscriptions = Subscription.objects.filter(user=request.user)
    selection = split_on_page(request, subscriptions)
    limit_page = selection['paginator'].num_pages
    check_paginator = page_out_of_paginator(request, limit_page)
    if check_paginator:
        redirect_path = generate_path(request, limit_page)
        return redirect(redirect_path)
    context = {'subscriptions': subscriptions, ** selection}
    return render(request, 'recipes/myFollow.html', context)


# страница рецепта
def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(
        request,
        'recipes/single_recipe.html',
        {'recipe': recipe},
    )


@login_required
def recipe_new(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        if save_recipe(request, form):
            return redirect('index')
    return render(request, 'recipes/formRecipe.html', {'form': form})


@login_required()
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe', id=recipe_id)
    form = RecipeForm(request.POST or None, files=request.FILES or None,
                      instance=recipe, initial={'author': request.user})
    tags = recipe.tags.all()
    ingredients = VolumeIngredient.objects.filter(recipe=recipe)
    context = {'form': form,
               'is_created': True,
               'recipe_id': recipe.id,
               'tags': tags,
               'ingredients': ingredients}
    if form.is_valid():
        form.save()
        return redirect('recipe', recipe.id)
    return render(request, 'recipes/formRecipe.html', context)


# @login_required
# def recipe_new(request):
#     form = RecipeForm(request.POST or None, files=request.FILES or None,
#                       initial={'author': request.user})
#     if form.is_valid():
#         form.save()
#         return redirect('index')
#     return render(request, 'recipes/formRecipe.html', {'form': form})


    # form = RecipeForm(request.POST or None, files=request.FILES or None)
    # if request.method == 'POST':
    #     ingredients = get_ingredients(request)
    #     if not ingredients:
    #         form.add_error(None, 'Должен быть хотя бы один ингредиент')
    #     elif form.is_valid():
    #         # recipe = form.save(commit=False)
    #         form.instance.author = request.user
    #         form.save()
    #         for title, amount in ingredients.items():
    #             VolumeIngredient.add_ingredient(form.instance, title, amount)
    #         return redirect('index')
    # form = RecipeForm()
    # context = {'form': form}
    # return render(request, 'recipes/formRecipe.html', context)

    
    # user = User.objects.get(username=request.user)
    # if request.method == 'POST':
    #     form = RecipeForm(request.POST or None, files=request.FILES or None)
    #     ingredients = get_ingredients(request)
    #     if not ingredients:
    #         form.add_error(None, 'Добавьте ингредиенты')
    #     elif form.is_valid():
    #         print(form.instance)
    #         form.instance.author = request.user
    #         form.save()
    #         for ing_name, amount in ingredients.items():
    #             ingredient = get_object_or_404(Ingredient, title=ing_name)
    #             recipe_ing = VolumeIngredient(
    #                 recipe=form.instance,
    #                 ingredient=ingredient,
    #                 quantity=amount
    #             )
    #             recipe_ing.save()
    #         form.save_m2m()
    #         return redirect('index')
    # else:
    #     form = RecipeForm()
    # return render(request, 'recipes/formRecipe.html', {'form': form})


# @login_required
# def recipe_edit(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)
#     if request.user != recipe.author:
#         return redirect('recipe', recipe_id=recipe.id)
#     if request.method == "POST":
#         form = RecipeForm(
#             request.POST or None,
#             files=request.FILES or None,
#             instance=recipe
#         )
#         ingredients = get_ingredients(request)
#         if form.is_valid():
#             # VolumeIngredient.objects.filter(recipe=recipe).delete()
#             recipe.volume_ingredient.all().delete()
#             recipe = form.save(commit=False)
#             recipe.author = request.user
#             recipe.save()
#             recipe.ingredients.all().delete()
#             for ing_name, quantity in ingredients.items():
#                 ingredient = get_object_or_404(Ingredient, title=ing_name)
#                 recipe_ing = VolumeIngredient(
#                     recipe=recipe,
#                     ingredient=ingredient,
#                     quantity=quantity
#                 )
#                 recipe_ing.save()
#             form.save_m2m()
#             return redirect('index')
#     form = RecipeForm(
#         request.POST or None,
#         files=request.FILES or None,
#         instance=recipe
#     )
#     return render(
#         request,
#         'recipes/formChangeRecipe.html',
#         {'form': form, 'recipe': recipe, }
    # )


# удаление рецепта
@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect('index')


# любимые рецепты пользователя
@login_required
def recipe_favor(request, username):
    favorites_list = Recipe.objects.user_favor(user=request.user)
    favorites_by_tags = get_recipes_by_tags(request, favorites_list)
    selection = split_on_page(request, favorites_by_tags.get('recipes'))
    limit_page = selection['paginator'].num_pages
    check_paginator = page_out_of_paginator(request, limit_page)
    if check_paginator:
        redirect_path = generate_path(request, limit_page)
        return redirect(redirect_path)
    return render(request, 'recipes/favorite.html', selection)


# список покупок
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
