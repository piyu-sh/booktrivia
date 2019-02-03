# Import the resource/controllers we're testing
from resources.book import *

# client is a fixture, injected by the `pytest-flask` plugin
def test_get_book(client):
    # Make a tes call to /books/1
    response = client.get("/books/1")

    # Validate the response
    assert response.status_code == 200
    assert response.json == {
        "id": 1, 
        "title": "Python for Dummies"
    }