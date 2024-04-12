import pytest
from news.models import News, Comment
from django.test.client import Client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Тайтл',
        text='Тетрадь смерти'
    )
    return news


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор коммента')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Никак не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(news, author):
    comm = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария!'
    )
    return comm


@pytest.fixture
def comment_pk(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'New text'
    }
