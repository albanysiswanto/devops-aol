import pytest
from app import app, init_db, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Use an in-memory database for testing unique to each test run
    # However, since app.py heavily relies on GLOBAL_CONN initialized at module level,
    # we might need to mock or be careful. 
    # For this simple test, we will use the test_client.
    
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Todo-App" in response.data or b"TODO-APP" in response.data
    assert b"Tambahkan Tugas Baru" in response.data

def test_add_task(client):
    """Test adding a task."""
    response = client.get('/addTask?task=TestTask', follow_redirects=True)
    assert response.status_code == 200
    assert b"TestTask" in response.data
