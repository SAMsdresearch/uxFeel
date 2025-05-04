import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample data generation for demonstration (replace with your actual dataframe)
data = {
    "Physician": ["Dr. Smith", "Dr. Smith", "Dr. Jones", "Dr. Jones", "Dr. Lee", "Dr. Lee"],
    "Clinic": ["Clinic A", "Clinic A", "Clinic A", "Clinic B", "Clinic B", "Clinic B"],
    "Issue": ["Issue1", "Issue2", "Issue1", "Issue2", "Issue1", "Issue2"],
    "Comment": [
        "Great service!",
        "Okay experience.",
        "Very bad experience.",
        "Could be better.",
        "Excellent care and attention.",
        "Not satisfied."
    ],
    "Stars": [5, 3, 1, 2, 5, 1],
    "Date": pd.to_datetime([
        "2024-04-01",
        "2024-04-02",
        "2024-04-03",
        "2024-04-04",
        "2024-04-05",
        "2024-04-06",
    ]),
    "Source": ["Google", "Google", "Yelp", "Yelp", "Google", "Yelp"],
    "class": ["Positive", "Neutral", "Negative", "Neutral", "Positive", "Negative"],
    "sentiment_score": [0.8, 0.0, -0.7, 0.1, 0.9, -0.9],
    "sentiment": ["positive", "neutral", "negative", "neutral", "positive", "negative"],
}

df = pd.DataFrame(data)

st.title("Physician Clinic Sentiment Analysis Dashboard")

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

st.subheader("Sentiment Count and Average Sentiment Score by Class")

if filtered_df.empty:
    st.write("No data available for the selected Clinic and Physician.")
else:
    # Aggregate sentiment count and average sentiment score for each class
    agg_df = filtered_df.groupby("class").agg(
        sentiment_count=("sentiment", "count"),
        avg_sentiment_score=("sentiment_score", "mean")
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = 'tab:blue'
    ax1.set_xlabel('Class')
    ax1.set_ylabel('Sentiment Count', color=color)
    ax1.bar(agg_df["class"], agg_df["sentiment_count"], color=color, alpha=0.6, label='Count')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Avg Sentiment Score', color=color)
    ax2.plot(agg_df["class"], agg_df["avg_sentiment_score"], color=color, marker='o', linestyle='-', label='Avg Sentiment Score')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(-1, 1)

    fig.tight_layout()
    st.pyplot(fig)

# Button to display positive and negative comments
if st.button("Show Positive and Negative Comments"):
    if filtered_df.empty:
        st.write("No comments to display for the selected filters.")
    else:
        pos_comments = filtered_df[filtered_df["sentiment"] == "positive"]
        neg_comments = filtered_df[filtered_df["sentiment"] == "negative"]

        st.markdown("### Positive Comments")
        if not pos_comments.empty:
            for idx, row in pos_comments.iterrows():
                st.write(f"- {row['Comment']} (Physician: {row['Physician']}, Clinic: {row['Clinic']})")
        else:
            st.write("No positive comments found.")

        st.markdown("### Negative Comments")
        if not neg_comments.empty:
            for idx, row in neg_comments.iterrows():
                st.write(f"- {row['Comment']} (Physician: {row['Physician']}, Clinic: {row['Clinic']})")
        else:
            st.write("No negative comments found.")
