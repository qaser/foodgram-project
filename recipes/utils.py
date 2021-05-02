from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


# словарь ингредиентов для корзины
def generate_purchase_cart(request):
    user = get_object_or_404(User, username=request.user.username)
    purchase_cart = user.purchases.all()
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
    for key, title in request.POST.items():
        if not key.startswith('nameIngredient_'):
            continue
        arg = key.split('_')[1]
        amount = request.POST['valueIngredient_' + arg]
        ingredients[title] = amount
    return ingredients
