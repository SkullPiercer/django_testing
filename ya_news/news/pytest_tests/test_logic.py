from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'New text'}
bad_form_data = {'text': f'Ты {choice(BAD_WORDS)} хахаха!'}


def test_user_can_create_comment(
        author_client, author, detail_url, news
):
    comments_count = Comment.objects.count()
    url = detail_url
    response = author_client.post(url, data=FORM_DATA)
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_cant_create_note(client, detail_url, login_url):
    comments_count = Comment.objects.count()
    url = detail_url
    response = client.post(url, data=FORM_DATA)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_bad_word_not_allowed_in_comment(
        author_client, detail_url
):
    comments_count = Comment.objects.count()
    url = detail_url
    response = author_client.post(url, data=bad_form_data)
    assertFormError(response, 'form', 'text', errors=[WARNING])
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(
        author_client, news, edit_url, comment, detail_url
):
    comment_from_db = Comment.objects.get(id=comment.id)
    url = edit_url
    response = author_client.post(url, data=FORM_DATA)
    news_url = detail_url
    redirect_url = f'{news_url}#comments'
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_not_author_cant_edit_comment(
        not_author_client, comment, edit_url
):
    url = edit_url
    response = not_author_client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
        author_client, news, delete_url, detail_url
):
    comments_count = Comment.objects.count()
    url = delete_url
    response = author_client.post(url)
    news_url = detail_url
    redirect_url = f'{news_url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == comments_count - 1


def test_not_author_cant_delete_note(not_author_client, delete_url):
    comments_count = Comment.objects.count()
    url = delete_url
    resource = not_author_client.post(url)
    assert resource.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count
