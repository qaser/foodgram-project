from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    password2 = None

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email')
