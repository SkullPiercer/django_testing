import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from django.urls import reverse


from news.models import Comment
from news.forms import WARNING, BAD_WORDS


def test_user_can_create_note(author_client, author, form_data, news_id):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_cant_create_note(client, form_data, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_bad_word_not_allowed_in_comment(
        author_client, form_data, news, news_id
):
    url = reverse('news:detail', args=news_id)
    form_data['text'] = f'Ты {BAD_WORDS[0]} хахаха!'
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=[WARNING])
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, news, comment_pk, comment, form_data
):
    url = reverse('news:edit', args=comment_pk)
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=(news.pk,))
    redirect_url = f'{news_url}#comments'
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_not_author_cant_edit_comment(
        not_author_client, news, comment_pk, comment, form_data
):
    url = reverse('news:edit', args=comment_pk)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text


def test_author_can_delete_comment(author_client, news, comment_pk):
    url = reverse('news:delete', args=comment_pk)
    response = author_client.post(url)
    news_url = reverse('news:detail', args=(news.pk,))
    redirect_url = f'{news_url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_not_author_cant_delete_note(not_author_client, comment_pk):
    url = reverse('news:delete', args=comment_pk)
    resource = not_author_client.post(url)
    assert resource.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
