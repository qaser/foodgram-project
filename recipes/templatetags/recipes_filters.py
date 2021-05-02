from django import template

from ..models import Favorite, Purchase, Subscription

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='get_filter_values')
def get_filter_values(value):
    return value.getlist('filters')


@register.filter(name='get_filter_link')
def get_filter_link(request, tag):
    new_request = request.GET.copy()
    if tag.value in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.value)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.value)
    return new_request.urlencode()


@register.filter(name='is_favorite')
def is_favorite(recipe, user):
    return Favorite.objects.filter(user=user, recipe=recipe).exists()


@register.filter(name='is_shop')
def is_shop(recipe, user):
    return Purchase.objects.filter(user=user, recipe=recipe).exists()


@register.filter(name='is_subscribe')
def is_follow(author, user):
    return Subscription.objects.filter(user=user, author=author).exists()


# склонение слова "рецепт"
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
