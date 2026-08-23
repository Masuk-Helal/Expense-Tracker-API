from test.test_main import client
from fastapi import status
import uuid

TEST_USERNAME = f'testuser_{uuid.uuid4().hex[:8]}'
TEST_EMAIL = f'{TEST_USERNAME}@example.com'
TEST_PASSWORD = 'StrongPass123'

access_token = None
transaction_id = None


def auth_headers():
    return {'Authorization': f'Bearer {access_token}'}


def test_register_and_login():
    global access_token

    register_response = client.post('/auth/register', json={
        'username': TEST_USERNAME,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
    })
    assert register_response.status_code == status.HTTP_201_CREATED
    assert 'hashed_password' not in register_response.json()

    login_response = client.post('/auth/login', data={
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD,
    })
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()['access_token']


def test_create_transaction():
    global transaction_id

    response = client.post('/transactions', json={
        'title': 'Salary',
        'amount': 5000,
        'type': 'income',
        'category': 'Job',
        'date': '2026-08-01',
    }, headers=auth_headers())

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == 'Salary'
    transaction_id = data['id']


def test_get_transactions():
    response = client.get('/transactions', headers=auth_headers())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


def test_get_specific_transaction():
    response = client.get(f'/transactions/{transaction_id}', headers=auth_headers())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == transaction_id


def test_update_transaction():
    response = client.put(f'/transactions/{transaction_id}', json={
        'amount': 5500,
    }, headers=auth_headers())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['amount'] == 5500


def test_delete_transaction():
    response = client.delete(f'/transactions/{transaction_id}', headers=auth_headers())
    assert response.status_code == status.HTTP_200_OK

    get_response = client.get(f'/transactions/{transaction_id}', headers=auth_headers())
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
