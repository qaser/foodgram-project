from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


# склонение слова "рецепт" (использую в follow_item.html)
@register.filter
def word_conjugate(number, args):
    args = [arg.strip() for arg in args.split(',')]
    last_digit = int(number) % 10
    eleven_fourteen = int(number) % 100
    if int(number) > 10 and eleven_fourteen in range(11,15):
        return f'{number} {args[2]}'  # рецептов
    if last_digit == 1:
        return f'{number} {args[0]}'  # рецепт
    if 1 < last_digit < 5:
        return f'{number} {args[1]}'  # рецепта
    return f'{number} {args[2]}'  # рецептов
