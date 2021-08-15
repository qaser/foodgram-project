from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


# склонение слова "рецепт" (использую в follow_item.html)
# args = 'рецепт,рецепта,рецептов'
@register.filter
def word_conjugate(number, args):
    args = [arg.strip() for arg in args.split(',')]
    int_num = int(number)
    last_digit = int_num % 10
    last_two_digit = int_num % 100  # для проверки 11...14
    if last_digit == 1 and last_two_digit != 11:
        return f'{number} {args[0]}'  # рецепт
    if 1 < last_digit < 5 and last_two_digit not in range(11, 15):
        return f'{number} {args[1]}'  # рецепта
    return f'{number} {args[2]}'  # рецептов
