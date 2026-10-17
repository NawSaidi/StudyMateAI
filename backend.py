
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

CORS(app, origins=[
    "http://localhost:5501",
    "http://127.0.0.1:5501"
])

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "StudyMate AI backend fonctionne avec l'IA locale !",
        "model": MODEL
    })


@app.route("/study", methods=["POST"])
def study():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    mode = data.get("mode", "explain")

    if not text:
        return jsonify({"answer": "Veuillez saisir un texte."}), 400

    if len(text) > 12000:
        return jsonify({
            "answer": "Texte trop long : limite de 12 000 caractères."
        }), 400

    if mode == "summary":
        instruction = (
            "Résume ce cours en français. Donne les idées principales "
            "de façon claire et fidèle au texte."
        )
    elif mode == "quiz":
        instruction = (
            "Crée 5 questions à choix multiples en français, avec 4 choix "
            "A, B, C, D pour chacune. Termine par le corrigé expliqué."
        )
    else:
        instruction = (
            "Explique ce cours en français à un débutant, avec des mots "
            "simples, des exemples concrets et des étapes claires."
        )

    prompt = f"""
Tu es StudyMate AI, un assistant pédagogique.
Réponds clairement en français.

Consigne : {instruction}

Texte de l'étudiant :
{text}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()

        if not answer:
            return jsonify({
                "answer": "L'IA n'a pas généré de réponse. Réessaie."
            }), 502

        return jsonify({
            "answer": answer,
            "mode": mode,
            "model": MODEL
        })

    except requests.exceptions.ConnectionError:
        return jsonify({
            "answer": "Ollama n'est pas accessible. Vérifie qu'il est lancé."
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "answer": "L'IA met trop de temps à répondre. Essaie un texte plus court."
        }), 504

    except requests.exceptions.RequestException as error:
        print("Erreur Ollama :", error)
        return jsonify({
            "answer": "Erreur pendant la génération par l'IA."
        }), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
