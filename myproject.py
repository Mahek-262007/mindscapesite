import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_calendar import calendar
import random
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Mindscape", layout="centered")

PROFILE_FILE = "users.csv"
MENTAL_FILE = "mental_health.csv"
TEST_FILE = "test_data.csv"

# ---------------- BEAUTIFUL GLOBAL STYLE ----------------
def set_bg(image_url):

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* Glass Card */
        div.block-container {{
            background: rgba(255,255,255,0.82);
            padding: 2rem;
            border-radius: 20px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}

        /* Fancy Buttons */
        .stButton>button {{
            width: 100%;
            height: 55px;
            border-radius: 15px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            color: white;
            background: linear-gradient(45deg,#ff6ec4,#7873f5);
            transition: 0.3s;
        }}

        .stButton>button:hover {{
            transform: scale(1.08);
            background: linear-gradient(45deg,#43e97b,#38f9d7);
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "Dashboard"


# ---------------- USER FUNCTIONS ----------------
def load_users():
    if os.path.exists(PROFILE_FILE):
        return pd.read_csv(PROFILE_FILE)
    return pd.DataFrame(columns=["Name","Gender","Phone","Email","Age","Password"])

def save_users(df):
    df.to_csv(PROFILE_FILE, index=False)


# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    set_bg("https://images.unsplash.com/photo-1507525428034-b723cf961d3e")

    st.title("🌸 Welcome to Mindscape 🌸")

    option = st.radio("Select Option", ["Login","Create Profile"])
    users = load_users()

    if option == "Login":

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = users[(users.Email == email) & (users.Password == password)]

            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user = user.iloc[0]
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        st.subheader("Create Profile")

        name = st.text_input("Name")
        gender = st.selectbox("Gender", ["Female","Male","Other"])
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        age = st.number_input("Age", 1, 100)
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            new = pd.DataFrame({
                "Name":[name],
                "Gender":[gender],
                "Phone":[phone],
                "Email":[email],
                "Age":[age],
                "Password":[password]
            })

            save_users(pd.concat([users,new], ignore_index=True))
            st.success("Profile Created!")


# ---------------- MAIN APP ----------------
else:

    user = st.session_state.user

    st.sidebar.title("👤 Profile")
    st.sidebar.write(user["Name"])
    st.sidebar.write(user["Email"])

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if st.session_state.page == "Dashboard":

        set_bg("https://images.unsplash.com/photo-1517836357463-d25dfeac3438")

        st.title("🏠 Your Wellness Hub")

        col1,col2 = st.columns(2)
        col3,col4 = st.columns(2)
        col5,col6 = st.columns(2)

        if col1.button("🧠 Mood Tracker"):
            st.session_state.page = "Mood"

        if col2.button("🩸 Period Tracker"):
            st.session_state.page = "Period"

        if col3.button("📖 Journal"):
            st.session_state.page = "Journal"

        if col4.button("✅ To-Do List"):
            st.session_state.page = "Todo"

        if col5.button("🧩 Weekly Tests"):
            st.session_state.page = "Tests"

        if col6.button("📊 Analytics"):
            st.session_state.page = "Analytics"


    # ---------------- MOOD ----------------
    elif st.session_state.page == "Mood":

        set_bg("https://images.unsplash.com/photo-1492724441997-5dc865305da7")

        st.title("🧠 Mood Tracker")

        mood_dict = {"😊":"Happy","😢":"Sad","😰":"Stressed","😌":"Calm"}

        emoji = st.radio("How are you feeling?", list(mood_dict.keys()), horizontal=True)
        mood = mood_dict[emoji]

        stress = st.slider("Stress Level", 0, 100, 30)
        sleep = st.slider("Sleep Hours", 0, 24, 7)

        if st.button("Save Mood"):

            new = pd.DataFrame({
                "Date":[str(date.today())],
                "Mood":[mood],
                "Stress":[stress],
                "Sleep":[sleep]
            })

            if os.path.exists(MENTAL_FILE):
                old = pd.read_csv(MENTAL_FILE)
                pd.concat([old,new], ignore_index=True).to_csv(MENTAL_FILE,index=False)
            else:
                new.to_csv(MENTAL_FILE,index=False)

            st.success("Mood Saved!")

        if os.path.exists(MENTAL_FILE):
            df = pd.read_csv(MENTAL_FILE)

            if "Mood" in df.columns:
                events = [{"title":str(r["Mood"]), "start":str(r["Date"])} for _,r in df.iterrows()]
                calendar(events=events)

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"


    # ---------------- PERIOD ----------------
    elif st.session_state.page == "Period":

        set_bg("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee")

        st.title("🩸 Period Tracker")

        if user["Gender"] != "Female":
            st.warning("Available only for females.")
        else:

            last_period = st.date_input("Last Period Date")
            cycle = st.slider("Cycle Length", 21, 35, 28)
            duration = st.slider("Period Duration", 3, 8, 5)

            today = date.today()
            days = (today - last_period).days
            cycle_day = (days % cycle) + 1
            next_period = last_period + timedelta(days=cycle)

            if cycle_day <= duration:
                phase = "Menstrual Phase"
            elif cycle_day <= 13:
                phase = "Follicular Phase"
            elif 14 <= cycle_day <= 16:
                phase = "Ovulation Phase"
            else:
                phase = "Luteal Phase"

            st.success(f"Cycle Day: {cycle_day}")
            st.info(f"Next Period: {next_period}")
            st.write("Current Phase:", phase)

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"


    # ---------------- JOURNAL ----------------
    elif st.session_state.page == "Journal":

        set_bg("https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d")

        st.title("📖 Personal Journal")

        mood_tag = st.selectbox("Mood Tag", ["😊 Happy","😢 Sad","😰 Stressed","😌 Calm"])
        text = st.text_area("Write Thoughts")

        if st.button("Save Entry") and text.strip():

            new = pd.DataFrame({
                "Date":[str(date.today())],
                "Mood":[mood_tag],
                "Journal":[text]
            })

            if os.path.exists("journal.csv"):
                old = pd.read_csv("journal.csv")
                pd.concat([old,new], ignore_index=True).to_csv("journal.csv",index=False)
            else:
                new.to_csv("journal.csv",index=False)

            st.success("Journal Saved!")

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"


    # ---------------- TODO ----------------
    elif st.session_state.page == "Todo":

        set_bg("https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b")

        st.title("✅ Smart To-Do List")

        task = st.text_input("Task")
        priority = st.selectbox("Priority", ["🔥 High","⭐ Medium","🌱 Low"])

        if st.button("Add Task") and task.strip():

            new = pd.DataFrame({
                "Task":[task],
                "Priority":[priority],
                "Completed":[False]
            })

            if os.path.exists("todo.csv"):
                old = pd.read_csv("todo.csv")
                pd.concat([old,new], ignore_index=True).to_csv("todo.csv",index=False)
            else:
                new.to_csv("todo.csv",index=False)

        if os.path.exists("todo.csv"):

            df = pd.read_csv("todo.csv")

            for i,row in df.iterrows():

                col1,col2 = st.columns([5,1])

                done = col1.checkbox(
                    f"{row['Task']} ({row['Priority']})",
                    value=row["Completed"],
                    key=f"t{i}"
                )

                if done != row["Completed"]:
                    df.at[i,"Completed"] = done
                    df.to_csv("todo.csv",index=False)
                    st.rerun()

                if col2.button("❌", key=f"d{i}"):
                    df.drop(i,inplace=True)
                    df.to_csv("todo.csv",index=False)
                    st.rerun()

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"


    # ---------------- TESTS ----------------
    elif st.session_state.page == "Tests":

        set_bg("https://images.unsplash.com/photo-1519681393784-d120267933ba")

        st.title("🧩 Brain Mini Games")

        word = random.choice(["TREE","APPLE","HOUSE","RIVER"])
        st.write("Remember:", word)

        ans = st.text_input("Type word")

        a,b = random.randint(1,10), random.randint(1,10)
        math_ans = st.number_input(f"{a}+{b}",0)

        if st.button("Submit"):

            score = 0
            if ans.upper() == word:
                score += 1
            if math_ans == a+b:
                score += 1

            st.success(f"Score: {score}/2")

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"


    # ---------------- ANALYTICS ----------------
    elif st.session_state.page == "Analytics":

        set_bg("https://images.unsplash.com/photo-1551288049-bebda4e38f71")

        st.title("📊 Wellness Analytics")

        if os.path.exists(MENTAL_FILE):

            df = pd.read_csv(MENTAL_FILE)

            if "Stress" in df.columns:
                st.line_chart(df["Stress"])

            if "Sleep" in df.columns:
                st.line_chart(df["Sleep"])

            if "Mood" in df.columns:
                st.bar_chart(df["Mood"].value_counts())

        if st.button("⬅ Back"):
            st.session_state.page = "Dashboard"
