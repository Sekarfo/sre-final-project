from app import app

def test_todos_get():
    client = app.test_client()
    response = client.get('/todos')
    assert response.status_code == 200
