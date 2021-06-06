from foodgram.settings import LOGIN_REDIRECT_URL
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import RecipeForm
from .models import Recipe, Subscription, User
from .utils import check_paginator, split_on_page


# список рецептов для главной страницы
@cache_page(20, key_prefix='index_page')
def index(request):
    active_tags = request.META['active_tags']
    recipes = Recipe.objects.get_by_tags(tag=active_tags, user=request.user)
    selection = split_on_page(request, recipes)
    context = {'filters': request.META['url_tail_tags'], **selection}
    template = 'recipes/index.html'
    return check_paginator(request, selection, template, context)


# страница автора рецептов
def profile(request, username):
    active_tags = request.META['active_tags']
    user = get_object_or_404(User, username=username)
    recipes = Recipe.objects.filter(
        author=user
    ).select_related('author').get_by_tags(tag=active_tags,user=request.user)
    selection = split_on_page(request, recipes)
    context = {
        'filters': request.META['url_tail_tags'],
        'author': user,
        **selection
    }
    template = 'recipes/authorRecipe.html'
    return check_paginator(request, selection, template, context)


# список подписок пользователя
@login_required(login_url=LOGIN_REDIRECT_URL)
def subscription_index(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    selection = split_on_page(request, subscriptions)
    context = {'subscriptions': subscriptions, ** selection}
    template = 'recipes/myFollow.html'
    return check_paginator(request, selection, template, context)


# любимые рецепты пользователя
@login_required(login_url=LOGIN_REDIRECT_URL)
def recipe_favor(request):
    active_tags = request.META['active_tags']
    favorites = Recipe.objects.user_favor(
        user=request.user).get_by_tags(
            tag=active_tags, user=request.user)
    selection = split_on_page(request, favorites)
    context = {'filters': request.META['url_tail_tags'], **selection}
    template = 'recipes/favorite.html'
    return check_paginator(request, selection, template, context)


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
@login_required(login_url=LOGIN_REDIRECT_URL)
def recipe_new(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('recipe_view', form.instance.id)
    return render(request, 'recipes/formRecipe.html', {'form': form})


# редактирование рецепта
@login_required(login_url=LOGIN_REDIRECT_URL)
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe_view', recipe_id)
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe  # использую в форме через kwargs
    )
    context = {'form': form, 'recipe': recipe}
    if form.is_valid():
        form.save()
        return redirect('recipe_view', recipe.id)
    return render(request, 'recipes/formRecipe.html', context)


# удаление рецепта
@login_required(login_url=LOGIN_REDIRECT_URL)
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect('index')


# список покупок
@login_required(login_url=LOGIN_REDIRECT_URL)
def purchase_cart(request):
    purchase = Recipe.objects.user_purchase(user=request.user)
    return render(
        request,
        'recipes/shopList.html',
        {'purchase': purchase}
    )


@login_required(login_url=LOGIN_REDIRECT_URL)
def purchase_save(request):
    lenght = 0
    title = 'recipe__ingredients__title'
    dimension = 'recipe__ingredients__dimension'
    quantity = 'recipe__volume_ingredient__quantity'
    ingredients = request.user.purchases.select_related('recipe').order_by(
        title).values(title, dimension).annotate(amount=Sum(quantity)).all()
    if not ingredients:
        return render(request, '/misc/400.html', status=400)
    text = 'Веб-приложение foody-doody.ru\n\nСписок покупок:\n\n'
    # определяю самое длинное название ингредиента
    for i in ingredients:
        if len(i[title]) > lenght:
            lenght = len(i[title])
    # генерирую текст списка ингредиентов
    for number, ingredient in enumerate(ingredients, start=1):
        amount = ingredient['amount']
        # для удобства чтения списка покупок делаю динамические отступы
        number_space = ('  ' if number < 10 else ' ')
        amount_space = '.' * (lenght - len(ingredient[title]) + 3)
        text = '{}{}'.format(
            text,
            f'{number}){number_space}{ingredient[title].capitalize()}'
            f'{amount_space}{amount}, {ingredient[dimension]}\n'
        )
    footer = "\n\nIt's Foody-Doody time!"
    text = '{}{}'.format(text, footer)
    response = HttpResponse(text, content_type='text/plain')
    filename = 'purchases.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
