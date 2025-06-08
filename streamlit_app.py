import streamlit as st
import json
import random
import time
from datetime import datetime

# Load question data
with open("final_questions_iosco.json", "r", encoding="utf-8") as f:
    all_questions = json.load(f)

investor_questions = [q for q in all_questions if q["category"] == "Financial Education"]
fininfluencer_questions = [q for q in all_questions if q["category"] == "Fininfluencer"]

# --- Password Protection ---
PASSWORD = "iloveaml2025"
def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password to continue", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password to continue", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        st.stop()

check_password()

# --- Game Initialization ---
st.title("💡 Financial Education & Fininfluencer Game")
st.markdown("Welcome to the AML Awareness Challenge!")

if "step" not in st.session_state:
    st.session_state.step = "start"
    st.session_state.name = ""
    st.session_state.role = ""
    st.session_state.questions = []
    st.session_state.score = 0
    st.session_state.index = 0
    st.session_state.start_time = None
    st.session_state.total_questions = 10

# --- Step 1: Welcome Screen ---
if st.session_state.step == "start":
    st.session_state.name = st.text_input("Enter your name:")
    st.session_state.role = st.radio("Choose your role:", ["Investor", "Fininfluencer"])
    if st.button("Next"):
        st.session_state.step = "count"
        st.rerun()

# --- Step 2: Choose number of questions ---
elif st.session_state.step == "count":
    st.session_state.total_questions = st.radio("How many questions do you want?", [10, 20])
    if st.button("Start Game"):
        pool = investor_questions if st.session_state.role == "Investor" else fininfluencer_questions
        st.session_state.questions = random.sample(pool, min(st.session_state.total_questions, len(pool)))
        st.session_state.score = 0
        st.session_state.index = 0
        st.session_state.start_time = time.time()
        st.session_state.step = "question"
        st.rerun()

# --- Step 3: Game Loop ---
elif st.session_state.step == "question":
    q = st.session_state.questions[st.session_state.index]
    index = st.session_state.index

    st.markdown(f"**Question {index + 1}/{st.session_state.total_questions}**")
    st.markdown(f"### {q['question']}")

    if f"answered_{index}" not in st.session_state:
        st.session_state[f"answered_{index}"] = False

    if not st.session_state[f"answered_{index}"]:
        selected = st.radio("Choose your answer:", q["options"], key=f"q{index}")
        if st.button("Submit Answer", key=f"submit_{index}"):
            st.session_state[f"answered_{index}"] = True
            if selected == q["correct_answer"]:
                st.success("Correct! ✅")
                st.session_state.score += 1
            else:
                st.error(f"Wrong! ❌ The correct answer was: {q['correct_answer']}")
            st.info(f"💬 Learn more: {q['advice']}  \n\n🔗 Source: {q['source']}")
    else:
        if st.button("Next Question", key=f"next_{index}"):
            st.session_state.index += 1
            if st.session_state.index >= st.session_state.total_questions:
                st.session_state.step = "result"
            st.rerun()

# --- Step 4: Result ---
elif st.session_state.step == "result":
    score = st.session_state.score
    total = st.session_state.total_questions
    percent = round(score / total * 100)
    duration = int(time.time() - st.session_state.start_time)

    st.markdown("## 🎉 Game Over!")
    st.markdown(f"**Name:** {st.session_state.name}")
    st.markdown(f"**Role:** {st.session_state.role}")
    st.markdown(f"**Score:** {score}/{total} ({percent}%)")
    st.markdown(f"**Duration:** {duration} seconds")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if percent >= 75:
        st.success("🏅 Congratulations! You earned a certificate!")
    else:
        st.warning("📘 Keep learning and try again!")

    if st.button("Replay"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Footer Disclaimer ---
st.markdown(
    "<hr style='margin-top: 50px;'><div style='text-align:center; font-size: 12px; color: grey;'>"
    "This is not an official IOSCO sponsored game - use for information purposes only - Copyright Guilhem ROS - 2025"
    "</div>",
    unsafe_allow_html=True
)
