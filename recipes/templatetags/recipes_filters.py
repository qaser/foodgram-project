from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


# генерация ссылки для тегов (использую в tags.html)
@register.filter(name='get_tag_link')
def get_tag_link(request, tag):
    new_request = request.GET.copy()
    if tag.value in request.META['active_tags']:
        filters = new_request.getlist('filters')
        filters.remove(tag.value)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.value)
    return new_request.urlencode()


# склонение слова "рецепт" (использую в follow_item.html)
@register.filter
def word_conjugate(number, args):
    args = [arg.strip() for arg in args.split(',')]
    last_digit = int(number) % 10
    eleven_fourteen = int(number) % 10
    if int(number) > 10 and eleven_fourteen in range(11,15):
        return f'{number} {args[2]}'  # рецептов
    if last_digit == 1:
        return f'{number} {args[0]}'  # рецепт
    if 1 < last_digit < 5:
        return f'{number} {args[1]}'  # рецепта
    return f'{number} {args[2]}'  # рецептов
