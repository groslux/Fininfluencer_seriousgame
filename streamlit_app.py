import streamlit as st
import json
import random
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Integrity Challenge",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Security / Password Gate using st.secrets ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Safety check to ensure secrets.toml is set up
    if "password" not in st.secrets:
        st.error("⚠️ System Error: Authentication secrets not configured. Please check your `.streamlit/secrets.toml` file.")
        st.stop()

    def password_entered():
        if st.session_state["password_input"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Clear from session state for security
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔒 Secure Access Required")
        st.text_input("Enter training password:", type="password", on_change=password_entered, key="password_input")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔒 Secure Access Required")
        st.text_input("Enter training password:", type="password", on_change=password_entered, key="password_input")
        st.error("❌ Incorrect password. Access denied.")
        st.stop()

check_password()

# --- Data Loading ---
@st.cache_data
def load_questions():
    try:
        with open("final_questions_iosco.json", "r", encoding="utf-8") as f:
            all_questions = json.load(f)
    except FileNotFoundError:
        st.warning("⚠️ Mission Data Offline: 'final_questions_iosco.json' not found. Load fallback protocols.")
        all_questions = []
        
    investor_q = [q for q in all_questions if q.get("category") == "Financial Education"]
    fininfluencer_q = [q for q in all_questions if q.get("category") == "Fininfluencer"]
    muling_q = [q for q in all_questions if q.get("category") == "Money Muling"]
    
    return investor_q, fininfluencer_q, muling_q

investor_questions, fininfluencer_questions, muling_questions = load_questions()

# --- Game State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = "start"
    st.session_state.player_name = ""
    st.session_state.module = ""
    st.session_state.questions = []
    st.session_state.score = 0
    st.session_state.current_index = 0
    st.session_state.start_time = None
    st.session_state.total_questions = 10

# --- App Header ---
st.title("🛡️ Financial Integrity Challenge")
st.markdown("Test your defenses against financial fraud, misleading influencers, and money laundering.")
st.divider()

# --- Step 1: Onboarding ---
if st.session_state.step == "start":
    st.subheader("Agent Registration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.player_name = st.text_input("Enter your operative name:")
    
    with col2:
        st.session_state.module = st.selectbox(
            "Select Training Module:", 
            ["Financial Education", "Fininfluencer Risks", "Money Muling"]
        )
        
    # UI Updated: Simulation strictly limited to a max of 10 questions to match the database limit.
    st.session_state.total_questions = st.select_slider(
        "Simulation Length (Questions):", 
        options=[3, 5, 8, 10], 
        value=10
    )

    if st.button("Initialize Simulation", type="primary", use_container_width=True):
        if not st.session_state.player_name:
            st.error("Protocol requires a valid operative name to continue.")
        else:
            # Map module selection to question pool
            if st.session_state.module == "Financial Education":
                pool = investor_questions
            elif st.session_state.module == "Fininfluencer Risks":
                pool = fininfluencer_questions
            else:
                pool = muling_questions
                
            # Adjust if JSON doesn't have enough questions
            actual_length = min(st.session_state.total_questions, len(pool))
            
            if actual_length == 0:
                st.error(f"Intel missing: No questions found for the '{st.session_state.module}' module in your database!")
            else:
                st.session_state.questions = random.sample(pool, actual_length)
                st.session_state.total_questions = actual_length
                st.session_state.score = 0
                st.session_state.current_index = 0
                st.session_state.start_time = time.time()
                st.session_state.step = "playing"
                st.rerun()

# --- Step 2: Game Loop ---
elif st.session_state.step == "playing":
    q_index = st.session_state.current_index
    total_q = st.session_state.total_questions
    current_q = st.session_state.questions[q_index]
    
    # Progress HUD
    progress = (q_index) / total_q
    st.progress(progress, text=f"Simulation Progress: {q_index}/{total_q}")
    
    # Question Display
    st.markdown(f"### Mission {q_index + 1}:")
    st.info(f"**{current_q['question']}**", icon="🎯")

    # State keys for the current question
    answered_key = f"answered_{q_index}"
    
    if answered_key not in st.session_state:
        st.session_state[answered_key] = False

    if not st.session_state[answered_key]:
        # User is answering
        selected_option = st.radio("Select your course of action:", current_q["options"], index=None)
        
        if st.button("Lock Answer", type="primary"):
            if selected_option is None:
                st.warning("You must select an option to proceed.")
            else:
                st.session_state[answered_key] = True
                st.session_state[f"selected_{q_index}"] = selected_option
                
                if selected_option == current_q["correct_answer"]:
                    st.session_state.score += 1
                st.rerun()
    else:
        # User has answered, show feedback
        selected = st.session_state[f"selected_{q_index}"]
        is_correct = (selected == current_q["correct_answer"])
        
        if is_correct:
            st.success(f"**Correct!** Strategy verified.", icon="✅")
        else:
            st.error(f"**Critical Failure!** The correct protocol was: {current_q['correct_answer']}", icon="❌")
            
        # Debriefing box
        with st.expander("📝 Debriefing & Intelligence", expanded=True):
            st.write(f"**Advice:** {current_q['advice']}")
            st.caption(f"🔗 Source: {current_q['source']}")
            
        if st.button("Next Mission ⏭️", use_container_width=True):
            st.session_state.current_index += 1
            if st.session_state.current_index >= total_q:
                st.session_state.step = "results"
            st.rerun()

# --- Step 3: Results Dashboard ---
elif st.session_state.step == "results":
    total_time = int(time.time() - st.session_state.start_time)
    win_rate = int((st.session_state.score / st.session_state.total_questions) * 100)
    
    if win_rate >= 75:
        st.balloons()
    else:
        st.snow()
    
    st.markdown(f"## 🏁 Simulation Complete, Agent {st.session_state.player_name}")
    
    # Metrics display
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", f"{st.session_state.score} / {st.session_state.total_questions}")
    col2.metric("Accuracy", f"{win_rate}%")
    col3.metric("Time Elapsed", f"{total_time} sec")
    
    st.divider()
    
    if win_rate >= 80:
        st.success("🏆 Excellent work. You are officially cleared for financial operations.")
    elif win_rate >= 50:
        st.warning("📊 Decent performance, but further study of the protocols is advised.")
    else:
        st.error("🚨 High Risk Operator. Immediate retraining required.")
        
    if st.button("🔄 Restart Simulation", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Footer ---
st.markdown(
    """
    <div style='text-align:center; margin-top: 50px; padding: 20px; font-size: 12px; color: grey; border-top: 1px solid #333;'>
        Not an official IOSCO sponsored tool. For educational and awareness purposes only.<br>
        © Guilhem ROS - 2025
    </div>
    """,
    unsafe_allow_html=True
)
