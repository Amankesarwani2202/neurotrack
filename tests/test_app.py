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
    assert "totalrounds = 3" in html


def test_famous_faces_is_removed_and_letter_search_uses_multiple_rounds(client):
    faces_response = client.get("/famous-faces")
    letter_response = client.get("/letter-search")
    assert faces_response.status_code == 404
    assert letter_response.status_code == 200

    letter_html = letter_response.get_data(as_text=True).lower()

    assert "totalrounds = 3" in letter_html


def test_participant_json_storage_and_unknown_history_nulls_scores(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATA_FILE", str(tmp_path / "participants.json"))
    response = client.post("/participants", json={
        "name": "Test Participant",
        "medical_history": "unknown",
        "age": 42,
        "gender": "Prefer not to say",
    })
    assert response.status_code == 201
    participant_id = response.get_json()["participant_id"]

    points = [{"x": index, "y": index * index, "t": index + 1} for index in range(12)]
    analysis = client.post("/analyze_all", json={
        "participant_id": participant_id,
        "medical_history": "unknown",
        "spiral": {"points": [{"round": 1, "points": points}]},
    })
    assert analysis.status_code == 200
    assert analysis.get_json()["spiral_details"]["spiral_score"] > 0
    assert analysis.get_json()["expected_score_factor"] is None
    assert client.get("/participants").get_json()[0]["test_scores"] is None


def test_cookie_theft_has_six_requested_options(client):
    response = client.get("/cookie-theft")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count("correct:true") == 1
    assert html.count('{id:') == 6
    assert "The woman is washing dishes." in html
    assert "The woman is washing clothes." in html
    assert "The kids are running." in html
    assert "The clothes are drying." in html
    assert "Someone is talking on the phone." in html
    assert "A dog is under the table." in html
