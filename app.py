import streamlit as st
from backend import bot

st.set_page_config(page_title="Health Buddy", page_icon="./logo.png", layout="centered")

SYSTEM_PROMPT = """You are a general health & wellness assistant.
- Answer only general wellness/health education questions (sleep, nutrition, exercise, hydration, BMI, etc.)
- Never diagnose, prescribe, or give medical advice.
- Keep answers clear, factual, 3-5 sentences.
- Use bullet points to break down data or lists.
- For symptoms/conditions, direct user to consult a doctor.
"""

st.markdown("""
<style>
.centered-header {
    text-align: center;
    margin-top: 3rem;
    margin-bottom: 2rem;
}
.centered-header h1 {
    font-size: 2.2rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 12px;
}
.pill-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 1rem;
}
div.stButton > button {
    border-radius: 20px;
    padding: 8px 18px;
    background: #1c1f26;
    color: #e5e7eb;
    border: 1px solid rgba(255,255,255,0.1);
    font-size: 14px;
}
div.stButton > button:hover {
    border-color: rgba(139,92,246,0.6);
    background: #23262f;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

quick_prompt = None

# ---- CENTERED HERO (only when empty) ----
if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("./logo.png", width=50)
        st.markdown(
            "<div class='centered-header'><h1>Health Buddy</h1></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:#9ca3af; margin-top:-1.5rem;'>Your AI health & wellness companion</p>",
            unsafe_allow_html=True
        )

        # centered form input (mimics chat_input but positioned here)
        with st.form("home_input", clear_on_submit=True):
            typed = st.text_input("", placeholder="How can I help you today?", label_visibility="collapsed")
            submitted = st.form_submit_button("Send")
        if submitted and typed:
            quick_prompt = typed

        # ---- PILL BUTTONS ----
        cards = [
            ("😴 Sleep", "What are some simple tips for better sleep hygiene?"),
            ("💧 Hydration", "How much water should I drink daily?"),
            ("⚖️ BMI", "What is BMI and how is it calculated?"),
            ("🏃 Exercise", "What are simple exercises for staying fit?"),
            ("🥗 Nutrition", "What are the basics of good nutrition?"),
            ("🧠 Stress", "What are some tips to manage stress and mental wellness?"),
        ]
        pcols = st.columns(3)
        for i, (label, question) in enumerate(cards):
            with pcols[i % 3]:
                if st.button(label, key=f"pill_{i}"):
                    quick_prompt = question
else:
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image("./logo.png", width=32)
    with col2:
        st.markdown("<h4 style='margin:0;'>Health Buddy</h4>", unsafe_allow_html=True)


# ---- CHAT HISTORY ----
for i, msg in enumerate(st.session_state.messages):

    if msg["role"] == "user":
        edit_key = f"editing_{i}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        with st.chat_message("user"):
            if st.session_state[edit_key]:
                new_text = st.text_area("Edit message", value=msg["content"], key=f"edit_input_{i}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Save & Resend", key=f"save_{i}"):
                        st.session_state.messages[i]["content"] = new_text
                        st.session_state.messages = st.session_state.messages[:i+1]  # drop everything after
                        st.session_state[edit_key] = False
                        with st.spinner("Thinking..."):
                            answer = bot(new_text, SYSTEM_PROMPT)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_{i}"):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                st.markdown(msg["content"])
                if st.button("✏️ Edit", key=f"edit_btn_{i}"):
                    st.session_state[edit_key] = True
                    st.rerun()

    else:  # assistant
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
            if i == len(st.session_state.messages) - 1:
                if st.button("🔄 Regenerate", key=f"regen_{i}"):
                    last_user_msg = st.session_state.messages[i-1]["content"]
                    st.session_state.messages.pop()
                    with st.spinner("Thinking..."):
                        new_answer = bot(last_user_msg, SYSTEM_PROMPT)
                    st.session_state.messages.append({"role": "assistant", "content": new_answer})
                    st.rerun()

# ---- BOTTOM CHAT INPUT (once conversation started) ----
query = None
if len(st.session_state.messages) > 0:
    query = st.chat_input("Ask a health/wellness question...")

final_query = query or quick_prompt

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = bot(final_query, SYSTEM_PROMPT)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()