import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Physician Clinic Sentiment Analysis Dashboard")

# Load data from Excel file
df = pd.read_excel('result_uxfeel.xlsx')


# Dropdown for Clinic
clinic_selected = st.selectbox(
    "Select Clinic",
    options=["All"] + sorted(df["Clinic"].dropna().unique().tolist())
)

# Filter physicians based on clinic selection
if clinic_selected == "All":
    physicians = df["Physician"].dropna().unique()
else:
    physicians = df[df["Clinic"] == clinic_selected]["Physician"].dropna().unique()

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

st.subheader("Sentiment Counts for Positive and Negative per Class")

if filtered_df.empty:
    st.write("No data available for the selected Clinic and Physician.")
else:
    # Group by class and sentiment, count entries
    count_df = filtered_df[filtered_df["sentiment"].isin(["positive", "negative"])].groupby(
        ["class", "sentiment"]
    ).size().unstack(fill_value=0)

    # Sort classes alphabetically to keep order consistent
    count_df = count_df.reindex(sorted(count_df.index))

    # Plot grouped bar chart for positive and negative counts per class
    ax = count_df.plot(kind='bar', figsize=(8,5), color={"positive": "green", "negative": "red"})

    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    ax.set_title("Count of Positive and Negative Sentiments per Class")
    ax.legend(title="Sentiment")
    plt.xticks(rotation=0)
    st.pyplot(ax.figure)

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
