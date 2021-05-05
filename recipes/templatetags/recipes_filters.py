from django import template

from ..models import Favorite, Purchase, Subscription, Recipe

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


# генерация ссылки для тегов (использую в tags.html)
@register.filter(name='get_tag_link')
def get_tag_link(request, tag):
    new_request = request.GET.copy()
    if tag.value in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.value)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.value)
    return new_request.urlencode()


# @register.filter(name='is_favorite')
# def is_favorite(recipe, user):
#     a = Recipe.objects.all().is_annotated(user=user)
#     for i in a:
#         print(i.in_favored)
#     # print(a)
#     # return Recipe.objects.is_annotated(user=user)
#     return Recipe.objects.all().is_annotated(user=user)


# @register.filter(name='is_shop')
# def is_shop(recipe, user):
#     return Purchase.objects.filter(user=user, recipe=recipe).exists()


@register.filter(name='is_subscribe')
def is_follow(author, user):
    return Subscription.objects.filter(user=user, author=author).exists()


# склонение слова "рецепт" (использую в follow_item.html)
@register.filter
def word_conjugate(number, args):
    args = [arg.strip() for arg in args.split(',')]
    last_digit = int(number) % 10
    if last_digit == 1:
        return f'{number} {args[0]}'
    elif 1 < last_digit < 5:
        return f'{number} {args[1]}'
    elif last_digit > 4 or last_digit == 0:
        return f'{number} {args[2]}'
