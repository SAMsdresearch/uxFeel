import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up():
    st.subheader("Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
    if st.button("Register"):
        users = load_users()
        if username in users:
            st.error("Username already exists. Please choose a different username.")
        elif not username or not password:
            st.error("Username and password cannot be empty.")
        elif password != password_confirm:
            st.error("Passwords do not match.")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success("User registered successfully! Please sign in.")
            st.session_state.signup_done = True

def sign_in():
    st.subheader("Sign In")
    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")
    if st.button("Login"):
        users = load_users()
        if username in users and users[username] == hash_password(password):
            st.success(f"Welcome, {username}!")
            st.session_state.authenticated = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None

def main_app():
    data = pd.read_excel('result_uxfeel.xlsx')
    df = data

    # Set page background color via markdown with CSS
    # st.markdown(
    #     """
    #     style>
    #     .stApp {
    #         background-color: #f0f2f6;
    #     }
    #     /style>
    #     """,
    #     unsafe_allow_html=True
    # )

    st.title("Physician Clinic Sentiment Analysis Dashboard")

    # Ensure the 'Clinic' column is treated as string and drop NaN values
    df['Clinic'] = df['Clinic'].astype(str).replace('nan', '')  # Convert NaN to empty string
    df = df[df['Clinic'] != '']  # Drop empty strings

    # Dropdown for Clinic
    clinic_selected = st.selectbox(
        "Select Clinic",
        options=["All"] + sorted(df["Clinic"].unique().tolist())
    )

    # Filter physicians based on clinic selection
    if clinic_selected == "All":
        physicians = df["Physician"].unique()
    else:
        physicians = df[df["Clinic"] == clinic_selected]["Physician"].unique()

    # Dropdown for Physician
    physician_selected = st.selectbox(
        "Select Physician",
        options=["All"] + sorted(physicians.tolist())
    )

    # Filter dataframe based on selections
    filtered_df = df.copy()

    if clinic_selected != "All":
        filtered_df = filtered_df[filtered_df["Clinic"] == clinic_selected]

    if physician_selected != "All":
        filtered_df = filtered_df[filtered_df["Physician"] == physician_selected]

    st.subheader("Sentiment Counts for Positive and Negative per Patient Journey Touch Points")

    if filtered_df.empty:
        st.write("No data available for the selected Clinic and Physician.")
    else:
        # Group by class and sentiment, count entries
        count_df = filtered_df[filtered_df["sentiment"].isin(["POSITIVE", "NEGATIVE"])].groupby(
            ["class", "sentiment"]
        ).size().unstack(fill_value=0)

        # Check if count_df is empty before plotting
        if count_df.empty:
            st.write("No positive or negative sentiments found for the selected filters.")
        else:
            # Sort classes alphabetically to keep order consistent
            count_df = count_df.reindex(sorted(count_df.index))

            # Define light red and light blue colors
            colors = {"POSITIVE": "#add8e6",  # light blue
                      "NEGATIVE": "#f7c6c5"}  # light red

            # Plot grouped bar chart for positive and negative counts per class with smaller size and font
            fig, ax = plt.subplots(figsize=(6, 4))
            count_df.plot(kind='bar', color=colors, ax=ax)

            ax.set_xlabel("Patient Journey Touch Points", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.set_title("Count of Positive and Negative Sentiments per Patient Journey Touch Points", fontsize=12)
            ax.legend(title="Sentiment", fontsize=9, title_fontsize=10)
            ax.tick_params(axis='x', labelrotation=0, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            st.pyplot(fig)

        # Pie chart for overall positive vs negative counts with reduced size
        total_counts = filtered_df[filtered_df["sentiment"].isin(["POSITIVE", "NEGATIVE"])].groupby(
            "sentiment").size()
        if not total_counts.empty:
            fig1, ax1 = plt.subplots(figsize=(4, 3))
            colors_pie = ["#add8e6", "#f7c6c5"]
            wedges, texts, autotexts = ax1.pie(
                total_counts,
                labels=total_counts.index,
                autopct='%1.1f%%',
                startangle=140,
                colors=colors_pie,
                textprops={'fontsize': 8}
            )
            ax1.axis('equal')
            st.subheader("Overall Positive vs Negative Sentiment Distribution")
            st.pyplot(fig1)

    # Button to display positive and negative comments
    if st.button("Show Positive and Negative Comments"):
        if filtered_df.empty:
            st.write("No comments to display for the selected filters.")
        else:
            pos_comments_df = filtered_df[filtered_df["sentiment"] == "POSITIVE"]
            neg_comments_df = filtered_df[filtered_df["sentiment"] == "NEGATIVE"]

            st.markdown("### Positive Comments")
            if not pos_comments_df.empty:
                for idx, row in pos_comments_df.iterrows():
                    st.write(f"- {row['Comment']} (Physician: {row['Physician']}, Clinic: {row['Clinic']})")
            else:
                st.write("No positive comments found.")

            st.markdown("### Negative Comments")
            if not neg_comments_df.empty:
                for idx, row in neg_comments_df.iterrows():
                    st.write(f"- {row['Comment']} (Physician: {row['Physician']}, Clinic: {row['Clinic']})")
            else:
                st.write("No negative comments found.")

def app():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'signup_done' not in st.session_state:
        st.session_state.signup_done = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    st.sidebar.title("User Authentication")

    if st.session_state.authenticated:
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
        if st.sidebar.button("Logout"):
            logout()
            st.experimental_rerun()
        main_app()
    else:
        menu = ["Login", "Sign Up"]
        choice = st.sidebar.selectbox("Select Action", menu)

        if choice == "Login":
            sign_in()
            if st.session_state.signup_done:
                st.session_state.signup_done = False
        elif choice == "Sign Up":
            sign_up()

if __name__ == "__main__":
    app()
