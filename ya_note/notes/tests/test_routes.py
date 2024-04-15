from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.author = User.objects.create(username='Sanya')
        cls.author_client = cls.client.force_login(cls.author)
        cls.another_user = User.objects.create(username='Randomich')
        cls.another_user_client = cls.client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title='Погулять',
            text='С собакой',
            slug='walking',
            author=cls.author
        )

    def test_availability_for_note_edit_delete(self):
        users = (
            (self.author_client, HTTPStatus.OK),
            (self.another_user_client, HTTPStatus.NOT_FOUND),
        )

        for user, status in users:
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )

        for url in urls:
            with self.subTest(url=url):
                page = reverse(url)
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages_availability(self):
        urls = (
            'notes:list',
            'notes:success',
            'notes:add'
        )
        for url in urls:
            page = reverse(url)
            response = self.author_client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)
