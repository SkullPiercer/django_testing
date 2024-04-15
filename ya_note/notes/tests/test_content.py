from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        notes = []
        cls.NUMBER_OF_NOTES = 10
        cls.url = reverse('notes:list')
        cls.user = User.objects.create(username='Randomich')
        cls.user_client = cls.client.force_login(cls.user)
        cls.not_author = User.objects.create(username='Not an Author')
        cls.not_author_client = cls.client.force_login(cls.not_author)
        for index in range(cls.NUMBER_OF_NOTES):
            note = Note(
                title=f'Новость номер {index}',
                text='text',
                slug=f'note{index}',
                author=cls.user
            )
            notes.append(note)
        Note.objects.bulk_create(notes)

    def test_content_on_page(self):
        response = self.user_client(self.url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertEqual(notes.count(), self.NUMBER_OF_NOTES)


class TestNoteCreatePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Randomich')
        cls.author_client = cls.client.force_login(cls.author)
        cls.other_user = User.objects.create(username='Other User')
        cls.other_user_client = cls.client.force_login(cls.other_user)
        cls.add_url = reverse('notes:add')
        cls.all_notes_url = reverse('notes:list')
        cls.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            slug='test-note',
            author=cls.author
        )

    def test_form(self):
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_single_note_in_list(self):
        response = self.author_client.get(self.all_notes_url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_user_notes_not_visible_to_other_users(self):
        response = self.other_user_client.get(self.all_notes_url)
        self.assertIn('object_list', response.context)
        self.assertNotIn(self.note, response.context['object_list'])
