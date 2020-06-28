import os
import tempfile

import pytest
import json

from sccontroller import create_app
from sccontroller.db import get_db, init_db
from sccontroller.template_controller import add_default_templates

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'rb') as f:
    _conf = json.loads(f.read())


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'NODE': _conf['GANACHE'],
        'DEFAULT_ACCOUNT': _conf['DEFAULT_ACCOUNT']
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
        add_default_templates()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth',
            json={'username': username, 'password': password},
        )

class AuthedClient(object):
    def __init__(self, client):
        self._client = client
        self._token = json.loads(self._client.post(
            '/auth',
            json={'username': "test", 'password': "test"},
        ).data)['access_token']

    def get(self, url):
        return self._client.get(
            url,
            headers={"Authorization": "JWT " + self._token},
        )

    def post(self, url, body):
        return self._client.post(
            url,
            headers={"Authorization": "JWT " + self._token},
            json=body,
        )



@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def authed_client(client):
    return AuthedClient(client)