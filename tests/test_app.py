import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app import app


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_nutrition_page():
    client = app.test_client()
    response = client.get("/nutrition")
    assert response.status_code == 200


def test_meals_page():
    client = app.test_client()
    response = client.get("/meals")
    assert response.status_code == 200


def test_shopping_page():
    client = app.test_client()
    response = client.get("/shopping")
    assert response.status_code == 200