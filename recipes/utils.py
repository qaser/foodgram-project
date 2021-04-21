from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


User = get_user_model()


def generate_purchase_cart(request):
    purchaser = get_object_or_404(User, username=request.user.username)
    purchase_cart = purchaser.purchase.all()
    ingredients = {}
    for item in purchase_cart:
        for j in item.recipe.volume_ingredient.all():
            name = f'{j.ingredient.title} ({j.ingredient.dimension})'
            quantity = j.quantity
            if name in ingredients.keys():
                ingredients[name] += quantity
            else:
                ingredients[name] = quantity
    result = []
    for key, quantity in ingredients.items():
        result.append(f'{key} - {quantity}')
    return result


def get_ingredients(request):
    ingredients = {}
    for key, ingredient_name in request.POST.items():
        if 'nameIngredient' in key:
            _ = key.split('_')
            ingredients[ingredient_name] = int(request.POST[
                f'valueIngredient_{_[1]}']
            )
    return ingredients
