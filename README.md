

\# StudyMate AI 📚



An AI-powered study assistant designed to help students learn more effectively.



\## Overview



StudyMate AI is a web application that helps students understand their courses using a locally running AI model. It connects a simple web interface to a Python Flask backend and Ollama.



\## Features



\- \*\*Course Summarization:\*\* Generate clear summaries of study materials.

\- \*\*Concept Explanation:\*\* Explain difficult topics in beginner-friendly language.

\- \*\*MCQ Quiz Generation:\*\* Generate multiple-choice questions with answers and explanations.

\- \*\*Local AI:\*\* Run inference locally with Ollama and Llama 3.2 (3B).

\- \*\*French Responses:\*\* Designed to support students learning in French.



\## Tech Stack



\- \*\*Frontend:\*\* HTML, CSS, JavaScript

\- \*\*Backend:\*\* Python, Flask, Flask-CORS

\- \*\*AI Runtime:\*\* Ollama

\- \*\*AI Model:\*\* `llama3.2:3b`

\- \*\*Version Control:\*\* Git and GitHub



\## Prerequisites



Install the following tools:



\- Python 3

\- Ollama

\- Git (optional, for cloning the repository)



Download Ollama: https://ollama.com/download



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/NawSaidi/StudyMateAI.git

cd StudyMateAI

```



\### 2. Download the AI model



```bash

ollama pull llama3.2:3b

```



Make sure Ollama is running on your computer.



\### 3. Create a Python virtual environment



On Windows CMD:



```cmd

python -m venv .venv

.venv\\Scripts\\activate.bat

```



\### 4. Install backend dependencies



```cmd

python -m pip install flask flask-cors requests

```



\### 5. Start the backend



```cmd

python backend.py

```



The backend runs at:



http://127.0.0.1:8000



\### 6. Start the frontend



Open a second CMD window in the project directory and run:



```cmd

python -m http.server 5501 --directory frontend-static

```



Open the application in your browser:



http://127.0.0.1:5501



\## Architecture



```text

Browser (HTML/CSS/JavaScript)

&#x20;           |

&#x20;           v

&#x20;      Flask Backend

&#x20;      Port 8000

&#x20;           |

&#x20;           v

&#x20;       Ollama API

&#x20;      Port 11434

&#x20;           |

&#x20;           v

&#x20;     Llama 3.2 (3B)

```



\## Important Notes



\- The AI model runs locally on the computer hosting the application.

\- Ollama must be running for AI features to work.

\- No OpenAI API key is required for this local setup.

\- The first response may take some time, depending on the computer.

\- The frontend and backend must both be running during local use.



\## Current Limitations



This is an early-stage project. Quiz generation currently returns questions and an answer key; interactive quiz scoring may be added in a future version.



\## Future Improvements



\- Improve the user interface and accessibility.

\- Add interactive quizzes and score tracking.

\- Add loading indicators and clearer error messages.

\- Prepare a secure, public online deployment.

\- Add automated tests.



\## Author



\*\*Nawres Saidi\*\*



GitHub: https://github.com/NawSaidi



\---



Built as a learning project to explore frontend development, Python backend development, and local AI integration.



