from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

import requests

app = Flask(__name__)


import os

CORS(
    app,
    origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        *[
            origin.strip()
            for origin in os.getenv("FRONTEND_ORIGIN", "").split(",")
            if origin.strip()
        ],
    ],
)


# Ollama is used locally by default.
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate",
)
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
MAX_TEXT_LENGTH = 12000

# Choose "ollama" locally or "gemini" in the cloud.
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def validate_text(data):
    """Validate the text sent by the frontend."""
    if not isinstance(data, dict):
        return None, "Les données envoyées sont invalides.", 400

    text = data.get("text", "")

    if not isinstance(text, str):
        return None, "Le texte doit être une chaîne de caractères.", 400

    text = text.strip()

    if not text:
        return None, "Veuillez saisir un texte.", 400

    if len(text) > MAX_TEXT_LENGTH:
        return None, "Le texte dépasse la limite de 12 000 caractères.", 400

    return text, None, None


def ask_gemini(prompt):
    """Send a prompt to Gemini through the official REST API."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "La clé Gemini n'est pas configurée. "
            "Définis la variable d'environnement GEMINI_API_KEY."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )

    try:
        response = requests.post(
            url,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                        ],
                    },
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(
                "Gemini n'a renvoyé aucune réponse exploitable."
            )

        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "\n".join(
            part["text"]
            for part in parts
            if isinstance(part, dict)
            and isinstance(part.get("text"), str)
        ).strip()

        if not answer:
            raise RuntimeError("Gemini a renvoyé une réponse vide.")

        return answer

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Gemini met trop de temps à répondre. Réessaie."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 0

        if status in (401, 403):
            message = (
                "Gemini a refusé la clé API. Vérifie sa configuration "
                "dans les variables d'environnement."
            )
        elif status == 429:
            message = (
                "La limite de requêtes Gemini est atteinte. "
                "Réessaie plus tard ou vérifie les limites de ton compte."
            )
        else:
            message = (
                f"Erreur HTTP Gemini ({status}). Vérifie le modèle "
                "et la configuration de l'API."
            )

        raise RuntimeError(message) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Impossible de contacter l'API Gemini. Vérifie ta connexion."
        ) from exc

    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(
            "La réponse de Gemini n'a pas le format attendu."
        ) from exc


def ask_ollama(prompt):
    """Send a prompt to the Ollama model running locally."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=240,
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()

        if not answer:
            raise RuntimeError(
                "Le modèle Ollama n'a renvoyé aucune réponse."
            )

        return answer

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Ollama est inaccessible. Vérifie qu'il est démarré."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "L'IA met trop de temps à répondre. Réessaie avec un texte plus court."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            "Ollama a renvoyé une erreur HTTP. Vérifie qu'il fonctionne "
            "et que le modèle est installé."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Erreur de communication avec Ollama."
        ) from exc

    except (ValueError, TypeError, AttributeError) as exc:
        raise RuntimeError(
            "La réponse d'Ollama n'a pas le format attendu."
        ) from exc


def ask_ai(prompt):
    """Use the configured AI provider."""
    if AI_PROVIDER == "gemini":
        return ask_gemini(prompt)

    if AI_PROVIDER == "ollama":
        return ask_ollama(prompt)

    raise RuntimeError(
        "Fournisseur IA inconnu. Utilise AI_PROVIDER=ollama ou AI_PROVIDER=gemini."
    )


def current_mode():
    """Return a stable mode label for the frontend."""
    return "gemini-cloud" if AI_PROVIDER == "gemini" else "ollama-local"


def run_ai(prompt):
    try:
        return {"answer": ask_ai(prompt), "mode": current_mode()}
    except RuntimeError as exc:
        app.logger.warning("Erreur IA (%s): %s", AI_PROVIDER, exc)
        return {"error": str(exc)}, 503


@app.route("/", methods=["GET"])
def home():
    provider = AI_PROVIDER
    if provider == "gemini":
        model = GEMINI_MODEL
        mode_label = "IA Gemini dans le cloud"
        configured = bool(GEMINI_API_KEY)
    elif provider == "ollama":
        model = MODEL
        mode_label = "IA locale avec Ollama"
        configured = True
    else:
        model = None
        mode_label = "Fournisseur IA non reconnu"
        configured = False

    return jsonify(
        {
            "message": "StudyMate AI backend fonctionne !",
            "mode": mode_label,
            "provider": provider,
            "model": model,
            "ai_live": configured,
            "features": ["summary", "chat", "quiz", "transform"],
        }
    )


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json(silent=True) or {}
    text, error, status = validate_text(data)

    if error:
        return jsonify({"error": error}), status

    prompt = f"""
Tu es StudyMate AI, un assistant pédagogique.
Réponds en français.
Résume le cours suivant en conservant les idées essentielles.
Utilise un titre, des points clés et les définitions importantes.
N'invente pas d'informations absentes du cours.

COURS :
{text}
"""
    result = run_ai(prompt)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    text, error, status = validate_text(data)

    if error:
        return jsonify({"error": error}), status

    question = data.get("question", "Explique ce cours simplement.")

    if not isinstance(question, str):
        return jsonify({"error": "La question doit être du texte."}), 400

    question = question.strip()[:1000]
    if not question:
        question = "Explique ce cours simplement."

    prompt = f"""
Tu es StudyMate AI, un professeur patient.
Réponds en français avec des mots simples.
Explique les concepts étape par étape et donne un exemple si utile.
Base-toi sur le cours fourni. Si une information manque, indique-le.

COURS :
{text}

QUESTION :
{question}
"""
    result = run_ai(prompt)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)


@app.route("/api/quiz", methods=["POST"])
def api_quiz():
    data = request.get_json(silent=True) or {}
    text, error, status = validate_text(data)

    if error:
        return jsonify({"error": error}), status

    prompt = f"""
Tu es StudyMate AI, un professeur qui crée des quiz pédagogiques.

À partir du cours fourni, crée exactement 5 questions QCM en français.
Chaque question doit avoir exactement 4 choix distincts et une seule
bonne réponse. Les mauvaises réponses doivent être plausibles.

Réponds uniquement avec un objet JSON valide, sans Markdown,
sans introduction et sans bloc de code, selon ce format :

{{
  "questions": [
    {{
      "question": "Texte de la question",
      "options": [
        "Première proposition",
        "Deuxième proposition",
        "Troisième proposition",
        "Quatrième proposition"
      ],
      "correct_index": 0,
      "explanation": "Explication de la bonne réponse."
    }}
  ]
}}

Règles :
- Le tableau questions contient exactement 5 questions.
- Chaque tableau options contient exactement 4 textes.
- correct_index est un entier de 0 à 3 indiquant la bonne réponse.
- explanation explique brièvement pourquoi cette réponse est correcte.
- Base les questions et les réponses sur le cours.
- N'invente pas de faits absents du cours.
- Ne donne pas la réponse dans le texte de la question.

COURS :
{text}
"""

    try:
        raw = ask_ai(prompt)
        cleaned = raw.strip()

        # Allow a JSON object surrounded by Markdown code fences.
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3].strip()

        # Recover the JSON object if the model added surrounding text.
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end < start:
            raise ValueError("Aucun objet JSON trouvé dans la réponse.")

        quiz = json.loads(cleaned[start : end + 1])
        questions = quiz.get("questions")

        if not isinstance(questions, list) or len(questions) != 5:
            raise ValueError("Le quiz doit contenir exactement 5 questions.")

        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Format de question incorrect.")

            if not isinstance(question.get("question"), str):
                raise ValueError("Texte de question manquant.")

            options = question.get("options")
            if (
                not isinstance(options, list)
                or len(options) != 4
                or not all(
                    isinstance(option, str) and option.strip()
                    for option in options
                )
                or len(set(options)) != 4
            ):
                raise ValueError(
                    "Chaque question doit avoir 4 choix distincts et valides."
                )

            correct = question.get("correct_index")
            if type(correct) is not int or correct not in range(4):
                raise ValueError("Indice de réponse incorrect.")

            if not isinstance(question.get("explanation"), str):
                raise ValueError("Explication manquante.")

        return jsonify(
            {
                "questions": questions,
                "mode": current_mode(),
            }
        )

    except RuntimeError as exc:
        app.logger.warning("Erreur IA lors de la création du quiz: %s", exc)
        return jsonify({"error": str(exc)}), 503

    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        app.logger.warning("Réponse de quiz invalide : %s", exc)
        return (
            jsonify(
                {
                    "error": (
                        "L'IA a renvoyé un quiz dans un format invalide. "
                        "Réessaie avec un cours plus court."
                    )
                }
            ),
            502,
        )


@app.route("/api/transform", methods=["POST"])
def api_transform():
    data = request.get_json(silent=True) or {}
    text, error, status = validate_text(data)

    if error:
        return jsonify({"error": error}), status

    action = data.get("action", "simplify")

    if action == "simplify":
        instruction = (
            "Simplifie le texte en français avec des mots courants. "
            "Conserve le sens, les faits et les informations importantes."
        )
    elif action == "translate":
        language = data.get("language", "anglais")

        if not isinstance(language, str):
            return jsonify({"error": "La langue doit être du texte."}), 400

        language = language.strip()[:50] or "anglais"
        instruction = (
            f"Traduis fidèlement le texte en {language}. "
            "Ne rajoute aucune information."
        )
    else:
        return jsonify({"error": "Action inconnue."}), 400

    prompt = f"""
Tu es un assistant de langue.
{instruction}

TEXTE :
{text}
"""
    result = run_ai(prompt)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)


@app.route("/study", methods=["POST"])
def study():
    """Keep compatibility with the previous interface."""
    data = request.get_json(silent=True) or {}
    text, error, status = validate_text(data)

    if error:
        return jsonify({"answer": error}), status

    mode = data.get("mode", "explain")

    if mode == "summary":
        prompt = (
            "Résume ce cours en français avec ses idées essentielles :\n\n"
            + text
        )
    elif mode == "quiz":
        prompt = (
            "Crée 5 QCM en français avec 4 choix par question, "
            "la bonne réponse et une explication :\n\n"
            + text
        )
    else:
        prompt = (
            "Explique ce cours en français simplement, étape par étape, "
            "avec un exemple :\n\n"
            + text
        )

    result = run_ai(prompt)

    if isinstance(result, tuple):
        return jsonify({"answer": result[0]["error"]}), result[1]

    return jsonify(
        {
            "answer": result["answer"],
            "mode": result["mode"],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
