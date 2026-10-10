import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from collections import Counter
from textblob import TextBlob


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Customer Review Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 17px;
    color: #6b7280;
    margin-bottom: 25px;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}

.section-title {
    font-size: 25px;
    font-weight: 650;
    margin-top: 15px;
}

.review-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    margin-bottom: 10px;
}

.small-text {
    color: #6b7280;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📊 Customer Review Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive customer feedback and sentiment analytics dashboard'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_csv(uploaded_file):

    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)

    possible_files = [
        "collected_data.csv",
        "./collected_data.csv"
    ]

    for file in possible_files:
        if os.path.exists(file):
            return pd.read_csv(file)

    return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Customer Review CSV",
    type=["csv"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("📌 Filters")


# ============================================================
# GET DATA
# ============================================================

df = load_csv(uploaded_file)

if df is None:

    st.warning(
        "No dataset found. Upload collected_data.csv from the sidebar."
    )

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "comment",
    "datetime"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        f"Missing required columns: {missing_columns}"
    )

    st.write("Available columns:")

    st.write(list(df.columns))

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

df["comment"] = df["comment"].fillna("").astype(str)

df["datetime"] = pd.to_datetime(
    df["datetime"],
    errors="coerce"
)

numeric_columns = [
    "comment_replies",
    "comment_retweets",
    "comment_likes"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# Remove empty comments

df = df[
    df["comment"].str.strip() != ""
].copy()


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

@st.cache_data
def calculate_sentiment(text_series):

    results = []

    for text in text_series:

        try:

            polarity = TextBlob(text).sentiment.polarity

        except Exception:

            polarity = 0

        if polarity > 0.05:

            sentiment = "Positive"

        elif polarity < -0.05:

            sentiment = "Negative"

        else:

            sentiment = "Neutral"

        results.append(
            (polarity, sentiment)
        )

    return results


sentiment_results = calculate_sentiment(
    df["comment"]
)


df["sentiment_score"] = [
    x[0] for x in sentiment_results
]

df["sentiment"] = [
    x[1] for x in sentiment_results
]


# ============================================================
# ADD DERIVED METRICS
# ============================================================

df["engagement"] = (
    df.get("comment_likes", 0)
    + df.get("comment_replies", 0)
    + df.get("comment_retweets", 0)
)

df["comment_length"] = (
    df["comment"]
    .str.len()
)

df["word_count"] = (
    df["comment"]
    .str.split()
    .str.len()
)

df["date"] = df["datetime"].dt.date


# ============================================================
# SIDEBAR FILTERS
# ============================================================

sentiment_options = [
    "All",
    "Positive",
    "Neutral",
    "Negative"
]

selected_sentiment = st.sidebar.selectbox(
    "Sentiment",
    sentiment_options
)


if "username" in df.columns:

    users = (
        df["username"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_users = st.sidebar.multiselect(
        "Users",
        users
    )

else:

    selected_users = []


# Date filter

valid_dates = df["date"].dropna()

if len(valid_dates) > 0:

    min_date = valid_dates.min()
    max_date = valid_dates.max()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date)
    )

else:

    date_range = None


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if selected_sentiment != "All":

    filtered_df = filtered_df[
        filtered_df["sentiment"]
        == selected_sentiment
    ]


if selected_users and "username" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["username"]
        .astype(str)
        .isin(selected_users)
    ]


if date_range and len(date_range) == 2:

    start_date = date_range[0]
    end_date = date_range[1]

    filtered_df = filtered_df[
        (filtered_df["date"] >= start_date)
        &
        (filtered_df["date"] <= end_date)
    ]


# ============================================================
# TOP KPI CARDS
# ============================================================

st.markdown(
    '<div class="section-title">📈 Executive Overview</div>',
    unsafe_allow_html=True
)

total_reviews = len(filtered_df)

positive_reviews = (
    filtered_df["sentiment"]
    .eq("Positive")
    .sum()
)

negative_reviews = (
    filtered_df["sentiment"]
    .eq("Negative")
    .sum()
)

neutral_reviews = (
    filtered_df["sentiment"]
    .eq("Neutral")
    .sum()
)

positive_percentage = (
    positive_reviews / total_reviews * 100
    if total_reviews > 0
    else 0
)

avg_sentiment = (
    filtered_df["sentiment_score"].mean()
    if total_reviews > 0
    else 0
)

total_engagement = (
    filtered_df["engagement"].sum()
    if total_reviews > 0
    else 0
)


k1, k2, k3, k4, k5, k6 = st.columns(6)


with k1:

    st.metric(
        "Total Reviews",
        f"{total_reviews:,}"
    )


with k2:

    st.metric(
        "Positive",
        f"{positive_reviews:,}"
    )


with k3:

    st.metric(
        "Negative",
        f"{negative_reviews:,}"
    )


with k4:

    st.metric(
        "Neutral",
        f"{neutral_reviews:,}"
    )


with k5:

    st.metric(
        "Positive %",
        f"{positive_percentage:.1f}%"
    )


with k6:

    st.metric(
        "Engagement",
        f"{total_engagement:,.0f}"
    )


# ============================================================
# SENTIMENT SECTION
# ============================================================

st.markdown(
    '<div class="section-title">😊 Sentiment Intelligence</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# SENTIMENT DONUT
# ------------------------------------------------------------

with col1:

    sentiment_counts = (
        filtered_df["sentiment"]
        .value_counts()
    )

    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        hole=0.55,
        title="Customer Sentiment Distribution"
    )

    fig.update_layout(
        height=420,
        legend_title="Sentiment"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# SENTIMENT SCORE
# ------------------------------------------------------------

with col2:

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_sentiment,
            title={
                "text": "Average Sentiment Score"
            },
            gauge={
                "axis": {
                    "range": [-1, 1]
                }
            }
        )
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# SENTIMENT OVER TIME
# ============================================================

st.markdown(
    '<div class="section-title">📅 Sentiment Trend</div>',
    unsafe_allow_html=True
)


daily_sentiment = (
    filtered_df
    .dropna(subset=["datetime"])
    .groupby(
        pd.Grouper(
            key="datetime",
            freq="D"
        )
    )
    .agg(
        average_sentiment=(
            "sentiment_score",
            "mean"
        ),
        review_count=(
            "comment",
            "count"
        )
    )
    .reset_index()
)


if len(daily_sentiment) > 0:

    fig = px.line(
        daily_sentiment,
        x="datetime",
        y="average_sentiment",
        markers=True,
        title="Average Customer Sentiment Over Time"
    )

    fig.add_hline(
        y=0,
        line_dash="dash"
    )

    fig.update_layout(
        height=450,
        yaxis_title="Sentiment Score",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# REVIEW VOLUME
# ============================================================

st.markdown(
    '<div class="section-title">📊 Review Volume</div>',
    unsafe_allow_html=True
)


if len(daily_sentiment) > 0:

    fig = px.bar(
        daily_sentiment,
        x="datetime",
        y="review_count",
        title="Number of Customer Reviews Over Time"
    )

    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Reviews"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ENGAGEMENT ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🔥 Customer Engagement</div>',
    unsafe_allow_html=True
)


if "comment_likes" in filtered_df.columns:

    engagement_col1, engagement_col2 = st.columns(2)


    with engagement_col1:

        fig = px.scatter(
            filtered_df,
            x="comment_likes",
            y="comment_retweets",
            size="comment_replies",
            color="sentiment",
            hover_data=[
                "comment"
            ],
            title="Likes vs Retweets"
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with engagement_col2:

        sentiment_engagement = (
            filtered_df
            .groupby("sentiment")["engagement"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            sentiment_engagement,
            x="sentiment",
            y="engagement",
            title="Average Engagement by Sentiment",
            text_auto=".1f"
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TOP CUSTOMER FEEDBACK
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Most Engaging Customer Feedback</div>',
    unsafe_allow_html=True
)


top_reviews = (
    filtered_df
    .sort_values(
        "engagement",
        ascending=False
    )
    .head(10)
)


display_columns = [
    column
    for column in [
        "username",
        "comment",
        "sentiment",
        "sentiment_score",
        "comment_likes",
        "comment_replies",
        "comment_retweets",
        "engagement"
    ]
    if column in top_reviews.columns
]


st.dataframe(
    top_reviews[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# POSITIVE / NEGATIVE FEEDBACK
# ============================================================

pos_col, neg_col = st.columns(2)


with pos_col:

    st.subheader("😊 Top Positive Reviews")

    positive_reviews_df = (
        filtered_df[
            filtered_df["sentiment"] == "Positive"
        ]
        .sort_values(
            "sentiment_score",
            ascending=False
        )
        .head(5)
    )

    for _, row in positive_reviews_df.iterrows():

        st.success(
            str(row["comment"])
        )


with neg_col:

    st.subheader("😡 Top Negative Reviews")

    negative_reviews_df = (
        filtered_df[
            filtered_df["sentiment"] == "Negative"
        ]
        .sort_values(
            "sentiment_score"
        )
        .head(5)
    )

    for _, row in negative_reviews_df.iterrows():

        st.error(
            str(row["comment"])
        )


# ============================================================
# REVIEW SEARCH
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Review Explorer</div>',
    unsafe_allow_html=True
)


search_text = st.text_input(
    "Search customer feedback",
    placeholder="Search keywords such as delivery, service, product..."
)


search_df = filtered_df.copy()


if search_text:

    search_df = search_df[
        search_df["comment"]
        .str.contains(
            search_text,
            case=False,
            na=False
        )
    ]


st.write(
    f"**{len(search_df):,} reviews found**"
)


st.dataframe(
    search_df[display_columns]
    if display_columns
    else search_df,
    use_container_width=True,
    hide_index=True,
    height=400
)


# ============================================================
# INDIVIDUAL REVIEW ANALYZER
# ============================================================

st.markdown(
    '<div class="section-title">🤖 Analyze a New Customer Review</div>',
    unsafe_allow_html=True
)


new_review = st.text_area(
    "Enter a customer review",
    placeholder=(
        "Example: The product quality was excellent "
        "and delivery was very fast!"
    ),
    height=120
)


if st.button(
    "🔍 Analyze Sentiment",
    type="primary"
):

    if not new_review.strip():

        st.warning(
            "Please enter a customer review."
        )

    else:

        result = TextBlob(
            new_review
        ).sentiment

        polarity = result.polarity
        subjectivity = result.subjectivity


        if polarity > 0.05:

            prediction = "Positive"

        elif polarity < -0.05:

            prediction = "Negative"

        else:

            prediction = "Neutral"


        a1, a2, a3 = st.columns(3)


        with a1:

            st.metric(
                "Prediction",
                prediction
            )


        with a2:

            st.metric(
                "Sentiment Score",
                f"{polarity:.2f}"
            )


        with a3:

            st.metric(
                "Subjectivity",
                f"{subjectivity:.2f}"
            )


        if prediction == "Positive":

            st.success(
                "😊 The review has a positive sentiment."
            )

        elif prediction == "Negative":

            st.error(
                "😡 The review has a negative sentiment."
            )

        else:

            st.info(
                "😐 The review has a neutral sentiment."
            )


# ============================================================
# DATA QUALITY
# ============================================================

st.markdown(
    '<div class="section-title">🧹 Data Quality</div>',
    unsafe_allow_html=True
)


dq1, dq2, dq3, dq4 = st.columns(4)


with dq1:

    st.metric(
        "Missing Values",
        int(filtered_df.isnull().sum().sum())
    )


with dq2:

    st.metric(
        "Duplicate Rows",
        int(filtered_df.duplicated().sum())
    )


with dq3:

    st.metric(
        "Avg Words / Review",
        f"{filtered_df['word_count'].mean():.1f}"
    )


with dq4:

    st.metric(
        "Avg Characters",
        f"{filtered_df['comment_length'].mean():.0f}"
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.markdown(
    '<div class="section-title">⬇️ Export Analysis</div>',
    unsafe_allow_html=True
)


download_df = filtered_df.copy()

csv_data = download_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download Analyzed Reviews",
    data=csv_data,
    file_name="customer_review_analysis.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Customer Review Intelligence Dashboard | "
    "Python • Streamlit • Pandas • Plotly • TextBlob"
)