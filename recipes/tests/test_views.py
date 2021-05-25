from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
# from PIL import Image

from ..models import User


class TestClient(TestCase):
    def setUp(self) -> None:
        print('Запуск браузера')
        self.nonauth_user = Client()
        self.auth_user = Client()
        # create user
        self.user = User.objects.create(
            username='cook'
        )
        self.auth_user.force_login(self.user)
        # create group 1

    def tearDown(self):
        print('Тест завершён')
        cache.clear()

    # # функция для хранения адресов тестируемых страниц
    # def check_urls(self, recipe, username):
    #     urls = [
    #         reverse('index'),
    #         reverse('profile', kwargs={'username': username}),
    #         reverse('subscriptions', kwargs={'username': username}),
    #         reverse(
    #             'recipe_view',
    #             kwargs={'recipe_id': recipe.id}
    #         )
    #     ]
    #     return urls

    # def selector_post_page(self, url, post):
    #     resp = self.client.get(url)
    #     self.assertEqual(resp.status_code, 200)
    #     if 'paginator' in resp.context:
    #         self.assertEqual(resp.context['paginator'].count, 1)
    #         count_post = resp.context['paginator'].object_list
    #         test_atr = count_post[0]
    #     else:
    #         test_atr = resp.context['post']
    #     self.assertEqual(test_atr.author, post.author)
    #     self.assertEqual(test_atr.text, post.text)
    #     self.assertEqual(test_atr.group, post.group)
    #     print(resp)

    # проверка создания профайла юзера
    def test_user_profile(self):
        resp = self.client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(resp.status_code, 200)

    # # проверка создания нового поста зарегистр. пользователем
    # def test_new_post_auth_user(self):
    #     resp = self.auth_user.post(
    #         reverse('new_post'),
    #         data={
    #             'author': self.user,
    #             'text': 'text and image',
    #             'group': self.group.id
    #         },
    #         follow=True
    #     )
    #     post = Post.objects.all()
    #     self.assertEqual(post.count(), 1)  # проверка наличия одного поста
    #     one_post = post[0]
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertEqual(one_post.author, self.user)  # проверка автора
    #     self.assertEqual(one_post.text, 'text and image')  # проверка текста
    #     self.assertEqual(one_post.group, self.group)  # проверка группы

    # # testing rendering new post on different page
    # def test_post_index(self):
    #     # create post
    #     post = Post.objects.create(
    #         text='Once...',
    #         author=self.user,
    #         group=self.group
    #     )
    #     urls = self.check_urls(post=post, group=self.group)
    #     for i in urls:
    #         with self.subTest(i=i):
    #             self.selector_post_page(url=i, post=post)

    # # проверка изменения поста автором
    # def test_post_user_edit(self):
    #     # create post
    #     post = Post.objects.create(
    #         text='Once...',
    #         author=self.user,
    #         group=self.group
    #     )
    #     # create group 2
    #     group_two = Group.objects.create(
    #         title='Tiste-Andi',
    #         slug='dragnipoor',
    #         description='Kill them all!'
    #     )
    #     self.auth_user.post(
    #         reverse('post_edit', kwargs={
    #             'username': post.author,
    #             'post_id': post.id}
    #         ),
    #         data={'text': '...all died', 'group': group_two.id},
    #         follow=True
    #     )
    #     post.refresh_from_db()  # обновляю пост из БД
    #     urls = self.check_urls(post=post, group=group_two)
    #     for i in urls:
    #         with self.subTest(i=i):
    #             self.selector_post_page(url=i, post=post)
    #     # проверка на отсутствие постов в первой группе
    #     resp = self.auth_user.get(
    #         reverse('group_name', kwargs={'slug': self.group.slug})
    #     )
    #     self.assertEqual(resp.context['paginator'].count, 0)

    # проверка перенаправления неавторизованного юзера
    # def test_post_nonauth_user(self):
    #     resp = self.nonauth_user.post(
    #         reverse('recipe_new'),
    #         data={'text': 'illegal text', 'group': self.group.id}
    #     )
    #     self.assertRedirects(
    #         resp,
    #         f"{reverse('login')}?next={reverse('new_post')}"
    #     )
    #     post = Post.objects.all()
    #     self.assertFalse(post.exists())

    # # проверка доступности группы
    # def test_exists_group(self):
    #     resp = self.auth_user.get(
    #         reverse('group_name', kwargs={'slug': self.group.slug})
    #     )
    #     self.assertEqual(resp.status_code, 200)

    def test_404(self):
        resp = self.client.get('/lost-site/')
        self.assertEqual(resp.status_code, 404)

    # def test_tag_img_include(self):
    #     img = Image.new('RGB', (900, 400))
    #     self.auth_user.post(
    #         reverse('new_post'),
    #         data={
    #             'author': self.user,
    #             'text': 'text and image',
    #             'group': self.group.id,
    #             'image': img
    #         },
    #         follow=True
    #     )
    #     post = Post.objects.first()
    #     urls = self.check_urls(post=post, group=self.group)
    #     for i in urls:
    #         with self.subTest(i=i):
    #             resp = self.client.get(i)
    #             self.assertEqual(resp.status_code, 200)
    #             self.assertContains(resp, 'img')

    # тест кеширования
    # def test_cache(self):
    #     # запрашиваем страницу
    #     self.auth_user.get(reverse('index'))
    #     # сразу пишем пост
    #     self.auth_user.post(
    #         reverse('new_post'),
    #         data={
    #             'author': self.user,
    #             'text': 'some text',
    #             'group': self.group.id,
    #         },
    #         follow=True
    #     )
    #     # вновь запрашиваем страницу
    #     resp = self.auth_user.get(reverse('index'))
    #     # profit
    #     self.assertNotContains(resp, 'some text')
