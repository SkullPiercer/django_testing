import pytest
from django.conf import settings
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import CommentForm


@pytest.mark.parametrize(
    'user', (
        (lf('author_client')),
        (lf('not_author_client')),
        (lf('client')),
    )
)
def test_home_page_content_for_all_users(user, db, homepage_news, home_url):
    url = home_url
    response = user.get(url)
    assert (len(response.context['object_list'])
            == settings.NEWS_COUNT_ON_HOME_PAGE)


@pytest.mark.parametrize(
    'user, form_on_page', (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form_on_page_for_different_users(
        user, db, form_on_page, news
):
    url = reverse('news:detail', args=(news.id,))
    response = user.get(url)
    if form_on_page:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context


def test_comment_form_on_edit_page(author_client, edit_url):
    url = edit_url
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_news_count_and_date(homepage_news, client, home_url):
    response = client.get(home_url)
    news_data = response.context['object_list']
    assert news_data.count() == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in news_data]
    sorted_news = sorted(all_dates, reverse=True)
    assert sorted_news == all_dates


@pytest.mark.django_db
def test_comments_are_sorted(comments, news, detail_url, client):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert sorted(all_timestamps) == all_timestamps
