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


def test_participant_json_storage_and_unknown_history_scores_are_saved(client, tmp_path, monkeypatch):
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
    saved = client.get("/participants").get_json()[0]
    assert saved["test_scores"]["Spiral_Score"] > 0
    assert saved["test_status"]["Reaction_Time_Score"] == "not_attempted"


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



def test_unattempted_tests_are_null_not_zero(client):
    response = client.post("/analyze_all", json={})
    assert response.status_code == 200
    result = response.get_json()
    assert result["subscores"]["Reaction_Time_Score"] is None
    assert result["subscores"]["Stroop_Score"] is None
    assert result["subscores"]["Memory_Score"] is None
    assert result["subscores"]["Clock_Drawing_Score"] is None
    assert result["risk_index"] is None


def test_stroop_zero_correct_never_gets_speed_bonus(client):
    response = client.post("/analyze_all", json={
        "stroop_correct": 0,
        "stroop_total": 8,
        "stroop_avg_rt": 0,
    })
    assert response.status_code == 200
    assert response.get_json()["subscores"]["Stroop_Score"] == 0


def test_registration_idempotency_key_prevents_duplicate_records(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATA_FILE", str(tmp_path / "participants.json"))
    payload = {
        "name": "Test Participant",
        "medical_history": "unknown",
        "age": 42,
        "gender": "Prefer not to say",
        "idempotency_key": "stable-test-key",
    }
    first = client.post("/participants", json=payload)
    second = client.post("/participants", json=payload)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.get_json()["participant_id"] == second.get_json()["participant_id"]
    assert len(client.get("/participants").get_json()) == 1


def test_excel_export_returns_workbook(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATA_FILE", str(tmp_path / "participants.json"))
    response = client.get("/export.xlsx")
    assert response.status_code == 200
    assert response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"



def test_csv_export_has_flattened_headers_and_rows(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATA_FILE", str(tmp_path / "participants.json"))
    from app import save_participants
    save_participants([{
        "id": 1, "name": "Scholar Example", "age": 16, "gender": "Prefer not to say",
        "medical_history": "unknown", "created_at": "2026-10-29T00:00:00Z",
        "test_scores": {"Memory_Score": 0, "Clock_Drawing_Score": None},
        "test_status": {"Memory_Score": "completed", "Clock_Drawing_Score": "not_attempted"},
        "raw_metrics": {"Memory_Correct_Ratio": "0/5"}, "risk_index": 100
    }])
    response = client.get("/export.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    content = response.get_data(as_text=True).lstrip("\ufeff")
    assert "score_Memory_Score" in content
    assert "test_status_Clock_Drawing_Score" in content
    assert "Scholar Example" in content
