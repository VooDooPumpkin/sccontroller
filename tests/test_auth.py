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
