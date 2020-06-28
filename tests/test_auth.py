import pytest
from flask import g, session, json


@pytest.mark.parametrize(('username', 'password', 'status', 'access_token'), (
    ('test', 'test', 200, True),
    ('test', 'a', 401, False),
    ('a', 'test', 401, False),
))
def test_login(auth, username, password, status, access_token):
    response = auth.login(username, password)
    assert response.status_code == status
    assert ('access_token' in json.loads(response.data)) == access_token

@pytest.mark.parametrize(('url', 'method'), (
    ('/templates', 'GET'),
    ('/templates/1', 'GET'),
    ('/create-cotract', 'POST'),
    ('/contracts', 'GET'),
    ('/contracts', 'POST'),
    ('/contracts/1', 'GET'),
    ('/contracts/<int:id>/destroy', 'GET'),
))
def test_authorization(authed_client, url, method):
    if method == 'GET':
        response = authed_client.get(url)
    elif method == 'POST':
        body = {}
        response = authed_client.post(url, body)

    assert response.status_code != 401

@pytest.mark.parametrize(('url', 'jwt_required', 'method'), (
    ('/auth', False, 'POST'),
    ('/templates', True, 'GET'),
    ('/templates/1', True, 'GET'),
    ('/create-cotract', True, 'POST'),
    ('/contracts', True, 'GET'),
    ('/contracts', True, 'POST'),
    ('/contracts/1', True, 'GET'),
    ('/contracts/1/destroy', True, 'GET'),
))
def test_authorization_crit(client, url, jwt_required, method):
    if method == 'GET':
        response = client.get(url)
    elif method == 'POST':
        body = {}
        response = client.post(url, json={"username": "test", "password": "test"})
    if jwt_required:
        assert response.status_code == 401
    else:
        assert response.status_code != 401