from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import User


# тесты в разработке
class TestClient(TestCase):
    def setUp(self) -> None:
        print('Запуск браузера')
        self.nonauth_user = Client()
        self.auth_user = Client()
        self.user = User.objects.create(
            username='cook'
        )
        self.auth_user.force_login(self.user)

    def tearDown(self):
        print('Тест завершён')
        cache.clear()

    # проверка создания профайла юзера
    def test_user_profile(self):
        resp = self.client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(resp.status_code, 200)

    def test_404(self):
        resp = self.client.get('/lost-page/')
        self.assertEqual(resp.status_code, 404)
