# StudyMate AI 📚

**A local AI-powered study assistant that helps students understand, summarize, and practice their course material.**

StudyMate AI is a learning project built with HTML, CSS, JavaScript, Python, Flask, and Ollama. It uses a locally running language model to provide study support without requiring a paid AI API key.

## Features

- **Course Summarization:** Turn course material into clear, structured summaries.
- **Concept Explanation:** Get beginner-friendly explanations of difficult topics.
- **Interactive MCQ Quizzes:** Generate five multiple-choice questions with four answer options each.
- **Automatic Scoring:** Submit answers, receive a score, and review the correct answers.
- **Answer Explanations:** Understand why each correct answer is right.
- **Local AI Inference:** Generate responses using Ollama and Llama 3.2 (3B).
- **French Learning Support:** Designed for students who study in French.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Cross-origin requests | Flask-CORS |
| AI runtime | Ollama |
| Language model | Llama 3.2 (3B) |
| Version control | Git, GitHub |

## Architecture

```text
User's Browser
      |
      v
HTML / CSS / JavaScript
      |
      | HTTP requests
      v
Python Flask Backend
127.0.0.1:8000
      |
      | Local API requests
      v
Ollama
127.0.0.1:11434
      |
      v
Llama 3.2 (3B)
```

## Prerequisites

Install the following software:

- Python 3
- Git
- Ollama

Download Ollama from [ollama.com/download](https://ollama.com/download).

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/NawSaidi/StudyMateAI.git
cd StudyMateAI
```

### 2. Download the AI model

```bash
ollama pull llama3.2:3b
```

Make sure Ollama is running before using the application.

### 3. Create and activate a virtual environment

On Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 4. Install the Python dependencies

```cmd
python -m pip install flask flask-cors requests
```

### 5. Start the backend

From the project root:

```cmd
python backend.py
```

The Flask backend should be available at:

`http://127.0.0.1:8000`

Keep this terminal open.

### 6. Start the frontend

Open a second CMD window and run:

```cmd
cd /d "%USERPROFILE%\Desktop\StudyMateAI"
.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1 --directory frontend-static
```

If you cloned the repository to a different folder, change the path accordingly.

Open the application in your browser:

`http://127.0.0.1:5500`

Keep this terminal open as well.

## How to Use

1. Open StudyMate AI in your browser.
2. Paste your course material into the input area.
3. Select a study feature.
4. Submit your course and wait for the local AI model.
5. For quizzes, answer the five questions and submit your choices to see your score and explanations.

## Privacy and Local Execution

- AI inference is performed through a locally running Ollama instance.
- No OpenAI API key is required for this configuration.
- The application requires the backend, frontend server, and Ollama to be running locally.
- Avoid entering sensitive personal information into any AI system.

## Current Limitations

- Response speed depends on the computer's hardware and the local model.
- AI-generated summaries, explanations, and quizzes may contain inaccuracies and should be checked against the original course material.
- Quiz results are displayed in the current session and are not saved to a database.
- The project is designed for local use; public deployment requires additional security, configuration, and testing.

## Roadmap

- Add automated backend tests.
- Improve accessibility and responsive behavior.
- Add persistent quiz history and progress tracking.
- Improve validation and error handling.
- Document a secure deployment workflow.

## Author

**Nawres Saidi**

GitHub: [@NawSaidi](https://github.com/NawSaidi)

---

*Built as a learning project to explore frontend development, Python backend development, and local AI integration.*
