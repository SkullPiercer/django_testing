# test_routes.py
from http import HTTPStatus

import pytest
from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('news_id')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
    )
)
def test_home_availability_for_anonymous_user(client, db, name):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
            ('news:delete', pytest.lazy_fixture('comment_pk')),
            ('news:edit', pytest.lazy_fixture('comment_pk')),
    )
)
def test_redirects(client, db, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )

)
@pytest.mark.parametrize(
    'name', 
    (
            'news:edit',
            'news:delete',
    )
)
def test_pages_availability_for_different_users(
        parametrized_client, expected_status, name, comment_pk
):
    url = reverse(name, args=comment_pk)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
