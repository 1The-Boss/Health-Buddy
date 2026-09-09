import streamlit as st
from backend import bot

st.set_page_config(page_title="Health Buddy", page_icon="./logo.png", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

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
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 1.5rem;
    margin-bottom: 0.3rem;
}
.centered-header h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 3.2rem;
    font-weight: 700;
    margin: 0;
}
.centered-header img {
    height: 65px;
    width: 65px;
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
    font-family: 'Times New Roman', Times, serif;
}
div.stButton > button:hover {
    border-color: rgba(139,92,246,0.6);
    background: #23262f;
}
</style>
""", unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("<style>[data-testid='stAppViewContainer']{overflow:hidden!important;height:100vh;}</style>", unsafe_allow_html=True)

quick_prompt = None

if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        import base64
        with open("./logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""<div class='centered-header'>
                <img src="data:image/png;base64,{logo_b64}">
                <h1>Health Buddy</h1>
            </div>""",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; font-family: Times New Roman, serif; color:#9ca3af; margin-top:0;'>Your AI health & wellness companion</p>",
            unsafe_allow_html=True
        )

        # centered form input (mimics chat_input but positioned here)
        with st.form("home_input", clear_on_submit=True):
            typed = st.text_input("", placeholder="How can I help you today?", label_visibility="collapsed")
            submitted = st.form_submit_button("Send")
        if submitted and typed:
            quick_prompt = typed

        # PILL BUTTONS
        cards = [
            ("😴 Sleep", "Simple tips for better sleep"),
            ("💧 Hydration", "How much water should I drink daily?"),
            ("⚖️ BMI", "What is BMI and how is it calculated?"),
            ("🏃 Exercise", "What are simple exercises for staying fit?"),
            ("🥗 Nutrition", "Give details on basics of good nutrition"),
            ("🧠 Stress", "Give some tips to manage stress and mental wellness"),
        ]
        pcols = st.columns(3)
        for i, (label, question) in enumerate(cards):
            with pcols[i % 3]:
                if st.button(label, key=f"pill_{i}"):
                    quick_prompt = question
else:
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image("./logo.png", width=50)
    with col2:
        st.markdown("<h4 style='margin:0;  font-family: Times New Roman, Times, serif; font-size: 2.25rem;'>Health Buddy</h4>", unsafe_allow_html=True)


# CHAT HISTORY 
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

    else:  
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

# CHAT INPUT
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