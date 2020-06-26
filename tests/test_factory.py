import os
import json
from sccontroller import create_app

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'rb') as f:
    _conf = json.loads(f.read())

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True,
                       'NODE': _conf['GANACHE'],
                       'DEFAULT_ACCOUNT': _conf['DEFAULT_ACCOUNT']
                       }).testing


# def test_hello(client):
#     response = client.get('/hello')
#     assert response.data == b'Hello, World!'