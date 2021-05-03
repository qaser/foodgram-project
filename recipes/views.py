from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from foodgram.settings import PAGINATOR_PAGES


from .forms import RecipeForm
from .models import (Ingredient, Purchase, Recipe, Subscription, User,
                     VolumeIngredient)
from .utils import generate_purchase_cart, get_ingredients


# function for split many recipes on pages
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return {'page': page, 'paginator': paginator}


@cache_page(20, key_prefix='index_page')
def index(request):
    tags = request.GET.getlist('filters')
    recipes_list = Recipe.objects.all()
    if tags:
        recipes_list = recipes_list.filter(tag__value__in=tags).distinct().all()
    selection = split_on_page(request, recipes_list)
    return render(request, 'recipes/index.html', selection)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    tags = request.GET.getlist('filters')
    recipes_list = user.recipes.all()
    if tags:
        recipes_list = recipes_list.filter(tag__value__in=tags)
    selection = split_on_page(request, recipes_list)
    sub = None
    if request.user.is_authenticated:
        sub = Subscription.objects.filter(
            user=request.user,
            author=user).exists()
    return render(
        request,
        'recipes/authorRecipe.html',
        {**{'profile': user, 'sub': sub}, **selection},
    )


@login_required
def subscription_index(request, username):
    user = get_object_or_404(User, username=username)
    # subs = Subscription.objects.filter(user=user).all()
    subs = user.follower.all()
    selection = split_on_page(request, subs)
    return render(
        request,
        'recipes/myFollow.html',
        selection,
    )


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # ingredients = recipe.volume_ingredient.all()
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
        ingredients = get_ingredients(request)  # функция вынесена в utils
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
    tag = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(
        favorite__user__id=request.user.id).all()
    if tag:
        recipe_list = recipe_list.filter(tag__value__in=tag).distinct()
    selection = split_on_page(request, recipe_list)
    return render(request, 'recipes/favorite.html', selection)


def purchase_cart(request):
    purchase = Purchase.objects.filter(user=request.user).all()
    return render(
        request,
        'recipes/shopList.html',
        {'purchase': purchase}
    )


@login_required
def purchase_save(request):
    result = generate_purchase_cart(request)  # функция вынесена в utils
    filename = 'ingredients.txt'
    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


@login_required
def purchases_download(request):
    title = 'recipe__ingredients__title'
    dimension = 'recipe__ingredients__dimension'
    quantity = 'recipe__ingredients_amounts__quantity'

    ingredients = request.user.purchases.select_related('recipe').order_by(
        title).values(title, dimension).annotate(amount=Sum(quantity)).all()

    if not ingredients:
        return render(request, 'misc/400.html', status=400)

    text = 'Список покупок:\n\n'
    for number, ingredient in enumerate(ingredients, start=1):
        amount = ingredient['amount']
        text += (
            f'{number}) '
            f'{ingredient[title]} - '
            f'{amount} '
            f'{ingredient[dimension]}\n'
        )

    response = HttpResponse(text, content_type='text/plain')
    filename = 'shopping_list.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response