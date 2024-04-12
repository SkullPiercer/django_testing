import pytest

from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.parametrize(
    'user',
    (
        (pytest.lazy_fixture('author_client')),
        (pytest.lazy_fixture('not_author_client')),
        (pytest.lazy_fixture('client')),
    )
)
def test_home_page_content_for_all_users(user, db, news):
    url = reverse('news:home')
    response = user.get(url)
    object_list = response.context['object_list']
    assert news in object_list
    assert len(object_list) == 1


@pytest.mark.parametrize(
    'user, form_on_page', (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form_on_page_for_different_users(
        user, db, form_on_page, news_id
):
    url = reverse('news:detail', args=news_id)
    response = user.get(url)
    if form_on_page:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context


def test_comment_form_on_edit_page(author_client, comment_pk):
    url = reverse('news:edit', args=comment_pk)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
