
import json

import pytest

import backend


@pytest.fixture
def client():
    backend.app.config["TESTING"] = True

    with backend.app.test_client() as test_client:
        yield test_client


def make_quiz():
    """Construit un quiz valide pour tester le backend sans Ollama."""
    questions = []

    for number in range(1, 6):
        questions.append({
            "question": f"Question de test {number} ?",
            "options": [
                "Réponse A",
                "Réponse B",
                "Réponse C",
                "Réponse D",
            ],
            "correct_index": 0,
            "explanation": "La réponse A est correcte pour ce test.",
        })

    return {"questions": questions}


def test_home_returns_backend_status(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()
    assert data["message"] == "StudyMate AI backend fonctionne !"
    assert "quiz" in data["features"]


def test_summarize_rejects_empty_text(client):
    response = client.post(
        "/api/summarize",
        json={"text": "   "},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_summarize_returns_ai_answer(client, monkeypatch):
    monkeypatch.setattr(
        backend,
        "ask_ai",
        lambda prompt: "Résumé simulé pour le test.",
    )

    response = client.post(
        "/api/summarize",
        json={"text": "Un cours de biologie."},
    )

    assert response.status_code == 200
    assert response.get_json()["answer"] == "Résumé simulé pour le test."
    assert response.get_json()["mode"] == "ollama-local"


def test_quiz_returns_five_questions(client, monkeypatch):
    quiz_json = json.dumps(make_quiz(), ensure_ascii=False)

    monkeypatch.setattr(
        backend,
        "ask_ai",
        lambda prompt: quiz_json,
    )

    response = client.post(
        "/api/quiz",
        json={"text": "Un cours utilisé pour le test."},
    )

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["questions"]) == 5

    for question in data["questions"]:
        assert len(question["options"]) == 4
        assert 0 <= question["correct_index"] <= 3
        assert question["explanation"]


def test_quiz_rejects_invalid_ai_json(client, monkeypatch):
    monkeypatch.setattr(
        backend,
        "ask_ai",
        lambda prompt: "Ceci n'est pas du JSON.",
    )

    response = client.post(
        "/api/quiz",
        json={"text": "Un cours utilisé pour le test."},
    )

    assert response.status_code == 502
    assert "error" in response.get_json()


def test_quiz_handles_unavailable_ai(client, monkeypatch):
    def fake_ask_ai(prompt):
        raise RuntimeError("Ollama est inaccessible.")

    monkeypatch.setattr(backend, "ask_ai", fake_ask_ai)

    response = client.post(
        "/api/quiz",
        json={"text": "Un cours utilisé pour le test."},
    )

    assert response.status_code == 503
    assert "error" in response.get_json()


def test_transform_rejects_unknown_action(client):
    response = client.post(
        "/api/transform",
        json={
            "text": "Un texte de test.",
            "action": "unknown",
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_chat_rejects_non_string_question(client):
    response = client.post(
        "/api/chat",
        json={
            "text": "Un cours de test.",
            "question": 123,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
