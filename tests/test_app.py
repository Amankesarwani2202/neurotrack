import pytest
from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page_does_not_promote_clock_draw_test(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Clock Drawing" not in html


def test_spiral_page_mentions_scale_and_three_rounds(client):
    response = client.get("/spiral")
    assert response.status_code == 200
    html = response.get_data(as_text=True).lower()
    assert "to scale" in html
    assert "3 rounds" in html


def test_famous_faces_and_letter_search_use_multiple_rounds(client):
    faces_response = client.get("/famous-faces")
    letter_response = client.get("/letter-search")
    assert faces_response.status_code == 200
    assert letter_response.status_code == 200

    faces_html = faces_response.get_data(as_text=True).lower()
    letter_html = letter_response.get_data(as_text=True).lower()

    assert "3 rounds" in faces_html
    assert "3 rounds" in letter_html
    assert "https://upload.wikimedia.org" in faces_html
