from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import RecipeForm
from .models import Recipe, Subscription, User, VolumeIngredient
from .utils import (generate_path, get_recipes_by_tags, page_out_of_paginator,
                    split_on_page)


# список рецептов для главной страницы
# @cache_page(20, key_prefix='index_page')
def index(request):
    recipe_list = Recipe.objects.all()
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    # выборка, разделённая на страницы
    selection = split_on_page(request, recipes_by_tags.get('recipes'))
    # извлекаю из пагинатора число получившихся страниц
    # затем проверяю номер страницы в запросе и сравниваю с лимитом
    # если запрос превышает лимит, то перенаправляю на
    # сгенерированный путь с последней доступной страницей и
    # выставленными фильтрами (тегами)
    # функции для этих манипуляций вынесены в утилиты
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
    recipe_list = Recipe.objects.filter(
        author=user
    ).is_annotated(
        request.user,
    ).distinct().select_related(
        'author'
    )
    recipes_by_tags = get_recipes_by_tags(request, recipe_list)
    selection = split_on_page(request, recipes_by_tags.get('recipes'))
    limit_page = selection['paginator'].num_pages
    check_paginator = page_out_of_paginator(request, limit_page)
    if check_paginator:
        redirect_path = generate_path(request, limit_page)
        return redirect(redirect_path)
    context = {'author': user, **selection}
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
    recipe = get_object_or_404(
        Recipe.objects.is_annotated(user=request.user),
        id=recipe_id
    )
    return render(
        request,
        'recipes/single_recipe.html',
        {'recipe': recipe},
    )


# новый рецепт
@login_required
def recipe_new(request):
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        initial={'request': request}
    )
    context = {'form': form}
    if request.method != 'POST':
        return render(request, 'recipes/formRecipe.html', context)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')


# редактирование рецепта
@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe_view', recipe_id)
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        initial={'request': request},
        instance=recipe
    )
    if request.method == 'POST':
        if form.is_valid():
            VolumeIngredient.objects.filter(recipe=recipe).delete()
            form.save()
            return redirect('recipe_view', recipe_id)
    return render(
        request,
        'recipes/formRecipe.html',
        {'form': form, 'recipe': recipe}
    )


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
    volume = 'recipe__volume_ingredient__volume'
    ingredients = request.user.purchases.select_related('recipe').order_by(
        title).values(title, dimension).annotate(amount=Sum(volume)).all()
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
