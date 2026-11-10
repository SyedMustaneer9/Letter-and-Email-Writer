# ✉️ Letter & Email Writer

An AI app that helps Pakistani students and job seekers write applications, letters and emails in **English, Urdu or Roman Urdu**.

## Features
- Choose the type: leave application, job application, complaint letter, email to a teacher, fee concession request and more
- Pick the language (English, Urdu, Roman Urdu) and the tone (formal, polite, urgent, friendly)
- Edit the result, download it as a text file
- One-click buttons: regenerate, make shorter, make more formal
- "Improve my draft" tab: paste your own letter and get a corrected version with a list of changes

## Built with
- [Streamlit](https://streamlit.io) for the web app
- [Groq API](https://groq.com) (Llama model) for the AI
- GitHub for hosting the code

## How to run on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt` and `README.md` to a GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app from that repository (main file: `app.py`).
3. Open **Advanced settings > Secrets** and add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
4. Click **Deploy**.

## Run on your own computer
```
pip install -r requirements.txt
streamlit run app.py
```
Create a file `.streamlit/secrets.toml` containing `GROQ_API_KEY = "your_key"` first.

## Note
AI can make mistakes. Always read the letter and fill in any `[bracketed]` details before sending.
