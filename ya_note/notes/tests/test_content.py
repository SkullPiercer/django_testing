from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        notes = []
        cls.url = reverse('notes:list')
        cls.user = User.objects.create(username='Randomich')
        for index in range(10):
            note = Note(
                title=f'Новость номер {index}',
                text='text',
                slug=f'note{index}',
                author=cls.user
            )
            notes.append(note)
        Note.objects.bulk_create(notes)

    def test_notes_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertEqual(notes.count(), 10)


class TestNoteCreatePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Randomich')
        cls.add_url = reverse('notes:add')

    def test_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
