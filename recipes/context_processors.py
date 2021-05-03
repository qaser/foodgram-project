from .models import Purchase, Tag


def all_tags(request):
    all_tags = Tag.objects.all()
    return {'all_tags': all_tags}


def url_parse(request):
    result_str = ''
    for item in request.GET.getlist('filters'):
        result_str += f'&filters={item}'
    return {'filters': result_str}


# def shop(request):
#     if request.user.is_authenticated:
#         shop_list = Purchase.objects.filter(user=request.user).values_list(
#             'recipe_id',
#             flat=True
#         )
#     else:
#         shop_list = []
#     return {'shop_list': shop_list}