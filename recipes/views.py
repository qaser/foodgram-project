from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Ingredient, RecipeIngredient, Recipe, User, Follow
from .forms import RecipeForm


# function for split many recipes on pages
def split_on_page(request, objects_on_page):
    paginator = Paginator(objects_on_page, 6)
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


def profile(request, username):
    user = get_object_or_404(User, username=username)
    recipe_author = user.recipes.all()
    selection = split_on_page(request, recipe_author)
    follow = None
    if request.user.is_authenticated:
        follow = Follow.objects.filter(
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
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.get(user=request.user, author=author)
    unfollow.delete()
    return redirect('profile', username=username)


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'recipes/formRecipe.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)