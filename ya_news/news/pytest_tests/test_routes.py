from http import HTTPStatus

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


STATUS_OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        lf('delete_url'),
        lf('edit_url'),
    )
)
def test_redirects(client, name, comment, login_url):
    login_url = login_url
    url = name
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (lf('home_url'), Client(), STATUS_OK),
        (lf('login_url'), Client(), STATUS_OK),
        (lf('logout_url'), Client(), STATUS_OK),
        (lf('signup_url'), Client(), STATUS_OK),
        (lf('detail_url'), Client(), STATUS_OK),
        (lf('edit_url'), lf('author_client'), STATUS_OK),
        (lf('delete_url'), lf('author_client'), STATUS_OK),
        (lf('edit_url'), lf('not_author_client'), NOT_FOUND),
        (lf('delete_url'), lf('not_author_client'), NOT_FOUND),
    )

)
def test_pages_available(reverse_url, parametrized_client, status):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status
