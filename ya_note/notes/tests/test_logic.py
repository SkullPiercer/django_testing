from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_SLUG = 'qwerty'

    @classmethod
    def setUpTestData(cls):
        cls.redirect_url = reverse('notes:success')
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Randomich')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Важное дело',
            'text': 'Купить майонез',
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.author, self.user)
        note_data = {
            'title': note.title,
            'text': note.text,
            'slug': note.slug
        }
        self.assertEqual(note_data, self.form_data)

    def test_user_cant_create_existing_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        second_note = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            second_note,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Ну очень важное дело'
    NEW_NOTE_TEXT = 'Дело по важнее'

    @classmethod
    def setUpTestData(cls):
        cls.redirect_url = reverse('notes:success')
        cls.note_author = User.objects.create(username='Randomich')
        cls.note_author_client = Client()
        cls.note_author_client.force_login(cls.note_author)
        cls.another_author = User.objects.create(username='Хулиган')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        cls.note = Note.objects.create(
            title='Тайтл',
            text=cls.NOTE_TEXT,
            slug='slugy',
            author=cls.note_author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Тайтл',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'slugy'
        }

    def test_author_can_delete_note(self):
        response = self.note_author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        response = self.note_author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_another_user_cant_delete_note(self):
        response = self.another_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_another_user_cant_edit_note(self):
        response = self.another_author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
