import os
from datetime import date

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------
# Page setup (must be the first Streamlit command)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Letter & Email Writer",
    page_icon="✉️",
    layout="centered",
)

# The app tries these models in order and uses the first one that works.
# Groq changes its model list often, so check console.groq.com/docs/models
# if all of them stop working, and replace the names below.
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
]

DOC_TYPES = [
    "Leave application",
    "Job application",
    "Complaint letter",
    "Email to teacher / principal",
    "Fee concession request",
    "Request letter",
    "Thank-you letter",
    "Custom (describe below)",
]

LANGUAGES = {
    "English": "English",
    "Urdu (اردو)": "Urdu, written in Urdu script",
    "Roman Urdu": "Roman Urdu (Urdu written with English letters)",
}

TONES = ["Formal", "Polite", "Urgent", "Friendly"]

WRITER_SYSTEM_PROMPT = (
    "You are an expert writer of letters, applications and emails for students "
    "and job seekers in Pakistan. Use the standard format people expect: date, "
    "recipient, subject line, salutation, clear body paragraphs, a respectful "
    "closing (for example 'Yours obediently' or 'Yours sincerely') and the "
    "sender's name. For emails, start with 'Subject:'. Never invent facts. If "
    "important information is missing, put a placeholder in square brackets, "
    "such as [Roll No.]. Output only the final letter or email, with no "
    "explanations before or after it."
)

IMPROVER_SYSTEM_PROMPT = (
    "You are a careful editor of letters, applications and emails for students "
    "and job seekers in Pakistan. Improve the draft the user gives you: fix "
    "grammar, spelling and structure, and adjust the tone as requested. Keep "
    "the original meaning and do not invent facts. Reply in exactly this "
    "format:\n\n"
    "### Improved version\n<the improved text>\n\n"
    "### What I changed\n<3 to 6 short bullet points, written in English>"
)


# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------
def get_client():
    """Create the Groq client using the key from Streamlit secrets."""
    key = None
    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)


def ask_ai(system_prompt, user_prompt):
    """Send a request to Groq and return the text, or None if it fails."""
    client = get_client()
    if client is None:
        st.error(
            "The Groq API key is missing. In Streamlit open Settings > Secrets "
            'and add: GROQ_API_KEY = "your_key_here"'
        )
        return None
    last_error = None
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.6,
            )
            text = response.choices[0].message.content or ""
            # Some models add their thinking inside <think> tags; remove it.
            if "</think>" in text:
                text = text.split("</think>")[-1]
            return text.strip()
        except Exception as error:
            last_error = error
            # If the model does not exist, try the next one in the list.
            if "model_not_found" in str(error) or "404" in str(error):
                continue
            break
    st.error(f"Sorry, the AI request failed. Please try again.\n\nDetails: {last_error}")
    return None


def init_state():
    """Set up the values we keep between button clicks."""
    st.session_state.setdefault("result", "")
    st.session_state.setdefault("version", 0)
    st.session_state.setdefault("language", "English")
    st.session_state.setdefault("tone", "Formal")


def set_result(text):
    """Store a new result and refresh the text box."""
    st.session_state["result"] = text
    st.session_state["version"] += 1
    st.rerun()


# ---------------------------------------------------------------
# Main app
# ---------------------------------------------------------------
init_state()

st.title("✉️ Letter & Email Writer")
st.caption(
    "Write applications, letters and emails in English, Urdu or Roman Urdu "
    "in a few seconds."
)

tab_write, tab_improve = st.tabs(["✍️ Write new", "🛠️ Improve my draft"])

# ----------------------------- Tab 1 ----------------------------
with tab_write:
    doc_type = st.selectbox("What do you want to write?", DOC_TYPES)

    col1, col2 = st.columns(2)
    with col1:
        sender = st.text_input("Your name")
    with col2:
        recipient = st.text_input(
            "Write to (person or office)",
            placeholder="e.g. The Principal, XYZ College",
        )

    reason = st.text_area(
        "Reason / main point",
        placeholder="e.g. I was ill with fever and need 3 days of leave.",
    )
    extra = st.text_input(
        "Extra details (optional)",
        placeholder="e.g. Class 10-B, Roll No. 25, dates 12 to 14 November",
    )

    col3, col4 = st.columns(2)
    with col3:
        language = st.selectbox("Language", list(LANGUAGES.keys()), key="language")
    with col4:
        tone = st.selectbox("Tone", TONES, key="tone")

    if st.button("Write it", type="primary", use_container_width=True):
        if not sender.strip() or not reason.strip():
            st.warning("Please fill in at least your name and the reason.")
        else:
            prompt = (
                f"Document type: {doc_type}\n"
                f"Sender name: {sender}\n"
                f"Recipient: {recipient or 'not given'}\n"
                f"Reason / main point: {reason}\n"
                f"Extra details: {extra or 'none'}\n"
                f"Today's date: {date.today().strftime('%d %B %Y')}\n"
                f"Language: {LANGUAGES[language]}\n"
                f"Tone: {tone}"
            )
            with st.spinner("Writing..."):
                text = ask_ai(WRITER_SYSTEM_PROMPT, prompt)
            if text:
                set_result(text)

    # Show the result (editable) with action buttons
    if st.session_state["result"]:
        st.subheader("Your letter")
        current_text = st.text_area(
            "You can edit the text here",
            value=st.session_state["result"],
            height=380,
            key=f"result_box_{st.session_state['version']}",
        )

        st.download_button(
            "⬇️ Download as .txt",
            data=current_text,
            file_name="letter.txt",
            mime="text/plain",
            use_container_width=True,
        )

        b1, b2, b3 = st.columns(3)
        rewrite_request = None
        if b1.button("🔄 Regenerate", use_container_width=True):
            rewrite_request = "Rewrite this with different wording but the same meaning."
        if b2.button("✂️ Make shorter", use_container_width=True):
            rewrite_request = "Make this shorter and more to the point."
        if b3.button("🎩 More formal", use_container_width=True):
            rewrite_request = "Make this more formal and respectful."

        if rewrite_request:
            prompt = (
                f"{rewrite_request}\n"
                f"Keep the language: {LANGUAGES[st.session_state['language']]}.\n\n"
                f"Text:\n{current_text}"
            )
            with st.spinner("Updating..."):
                text = ask_ai(WRITER_SYSTEM_PROMPT, prompt)
            if text:
                set_result(text)

# ----------------------------- Tab 2 ----------------------------
with tab_improve:
    draft = st.text_area(
        "Paste your own draft here",
        height=250,
        key="draft_input",
    )
    c1, c2 = st.columns(2)
    with c1:
        imp_language = st.selectbox(
            "Language of the result", list(LANGUAGES.keys()), key="imp_language"
        )
    with c2:
        imp_tone = st.selectbox("Tone", TONES, key="imp_tone")

    if st.button("Improve it", type="primary", use_container_width=True):
        if not draft.strip():
            st.warning("Please paste a draft first.")
        else:
            prompt = (
                f"Language: {LANGUAGES[imp_language]}\n"
                f"Tone: {imp_tone}\n\n"
                f"Draft:\n{draft}"
            )
            with st.spinner("Improving..."):
                improved = ask_ai(IMPROVER_SYSTEM_PROMPT, prompt)
            if improved:
                st.markdown(improved)

st.divider()
st.caption(
    "AI can make mistakes. Please read your letter carefully and fill in any "
    "[bracketed] details before sending."
)
