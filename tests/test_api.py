import json

def test_contracts(authed_client):
    response = authed_client.get('/contracts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list) and len(data) == 2
    assert set(data[0].keys()) == set(['id', 'template_id', 'address', 'status', 'users_guide', 'creator_guide'])

def test_contracts_subset(authed_client):
    response = authed_client.post('/contracts', {'ids': [1, 2]})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list) and len(data) == 2
    assert set(data[0].keys()) == set(['id', 'template_id', 'address', 'status', 'users_guide', 'creator_guide'])

def test_contract(authed_client):
    response = authed_client.get('/contracts/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict) and (set(data.keys()) == set(['id', 'template_id', 'address', 'status', 'users_guide', 'creator_guide']))
    assert data['id'] == 1

def test_contract_destruction(authed_client):
    response = authed_client.get('/contracts/1/destroy')
    assert response.status_code == 204
    response = authed_client.get('/contracts/1')
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == '"Contract with this id doesn\'t exist"'

def test_templates(authed_client):
    response = authed_client.get('/templates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list) and len(data) == 2
    assert set(data[0].keys()) == set(['id', 'name', 'description', 'parameters_list'])

def test_template(authed_client):
    response = authed_client.get('/templates/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict) and (set(data.keys()) == set(['id', 'name', 'description', 'parameters_list']))
    assert data['id'] == 1