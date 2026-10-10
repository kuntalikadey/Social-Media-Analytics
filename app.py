from flask import Flask, render_template, url_for, request, redirect, session

import dash
from dash import dcc, html, Input, Output

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from clean_collected_data import preprocess_data
from x_api import search_recent_posts, XAPIError
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

URL = ""
file_path = "./Customer-review-app/collected_data.csv"


# ============================================================
# DATA
# ============================================================

def get_data(search_query=None):
    """
    Load live X data when XFETCH_API_KEY is configured.

    If no token is configured, keep the existing local dataset available
    so the dashboard itself remains usable. No synthetic X posts are created.
    """
    if search_query and search_query.strip():
        token = os.getenv("XFETCH_API_KEY", "").strip()
        if not token:
            raise XAPIError(
                "XFETCH_API_KEY is not configured. Add your xfetch API key "
                "to the .env file before using live X search."
            )
        return search_recent_posts(search_query.strip(), token)

    data, small_data = preprocess_data()
    return data, small_data


# ============================================================
# FLASK SERVER
# ============================================================

server = Flask(__name__)
server.secret_key = "abc"


# ============================================================
# DASH APP
# ============================================================

dash_app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname="/dashboard/",
    title="Social Media Sentiment Analytics"
)


# ============================================================
# DASHBOARD LAYOUT
# ============================================================

dash_app.layout = html.Div(

    [

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        html.Div(
            [
                html.H1(
                    "Social Media Sentiment Analytics",
                    style={
                        "margin": "0",
                        "fontSize": "38px",
                        "fontWeight": "700"
                    }
                ),

                html.P(
                    "Customer feedback, sentiment and engagement analysis",
                    style={
                        "marginTop": "10px",
                        "fontSize": "18px",
                        "opacity": "0.9"
                    }
                )
            ],

            style={
                "background": "linear-gradient(135deg, #667eea, #764ba2)",
                "color": "white",
                "padding": "35px",
                "textAlign": "center",
                "borderRadius": "0 0 20px 20px",
                "marginBottom": "30px"
            }
        ),


        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        html.Div(
            id="kpi-container",

            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "12px",
                "justifyContent": "center",
                "margin": "20px 25px 35px 25px",
                "width": "calc(100% - 50px)",
                "boxSizing": "border-box"
            }
        ),



        # ----------------------------------------------------
        # LIVE X SEARCH + FILTERS
        # ----------------------------------------------------

        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Search X (live)",
                            style={
                                "fontWeight": "600",
                                "fontSize": "15px",
                                "marginBottom": "8px",
                                "display": "block"
                            }
                        ),
                        dcc.Input(
                            id="x-search",
                            type="text",
                            placeholder="e.g. AI, Virat Kohli, from:username",
                            value="",
                            debounce=True,
                            style={
                                "width": "100%",
                                "padding": "10px",
                                "border": "1px solid #ddd",
                                "borderRadius": "8px",
                                "boxSizing": "border-box"
                            }
                        )
                    ],
                    style={"width": "360px"}
                ),

                html.Div(
                    [
                        html.Label(
                            "Sentiment Filter",
                            style={
                                "fontWeight": "600",
                                "fontSize": "15px",
                                "marginBottom": "8px",
                                "display": "block"
                            }
                        ),

                        dcc.Dropdown(
                            id="sentiment-filter",
                            options=[
                                {"label": "All Sentiments", "value": "All"},
                                {"label": "Positive", "value": "Positive"},
                                {"label": "Neutral", "value": "Neutral"},
                                {"label": "Negative", "value": "Negative"}
                            ],
                            value="All",
                            clearable=False
                        )
                    ],
                    style={"width": "240px"}
                ),

                html.Div(
                    [
                        html.Label(
                            "Minimum Likes",
                            style={
                                "fontWeight": "600",
                                "fontSize": "15px",
                                "marginBottom": "8px",
                                "display": "block"
                            }
                        ),

                        dcc.Input(
                            id="minimum-likes",
                            type="number",
                            value=0,
                            min=0,
                            step=1,
                            style={
                                "width": "100%",
                                "padding": "10px",
                                "border": "1px solid #ddd",
                                "borderRadius": "8px",
                                "boxSizing": "border-box"
                            }
                        )
                    ],
                    style={"width": "180px"}
                ),

                html.Div(
                    id="data-source-status",
                    children="Using local dataset. Enter a search after configuring XFETCH_API_KEY.",
                    style={
                        "fontSize": "13px",
                        "color": "#666",
                        "maxWidth": "360px",
                        "lineHeight": "1.4"
                    }
                )
            ],

            style={
                "backgroundColor": "white",
                "padding": "20px 25px",
                "borderRadius": "15px",
                "margin": "0 40px 20px 40px",
                "display": "flex",
                "gap": "25px",
                "alignItems": "end",
                "flexWrap": "wrap",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),

        html.Div(
            id="live-error",
            style={
                "margin": "0 40px 20px 40px",
                "color": "#b00020",
                "fontWeight": "600"
            }
        ),

        # ----------------------------------------------------
        # SENTIMENT DISTRIBUTION
        # ----------------------------------------------------

        html.Div(
            [

                html.H2(
                    "Sentiment Overview",
                    style={
                        "marginBottom": "5px"
                    }
                ),

                html.P(
                    "Distribution of positive, neutral and negative user responses.",
                    style={
                        "color": "#666",
                        "marginBottom": "20px"
                    }
                ),

                dcc.Graph(
                    id="sentiment-distribution-chart"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),


        # ----------------------------------------------------
        # SENTIMENT OVER TIME
        # ----------------------------------------------------

        html.Div(
            [

                html.H2(
                    "Sentiment Analysis Over Time"
                ),

                html.P(
                    "How user sentiment changes across reply timestamps.",
                    style={
                        "color": "#666"
                    }
                ),

                dcc.Graph(
                    id="sentiment-time-series-chart"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),


        # ----------------------------------------------------
        # ENGAGEMENT ANALYSIS
        # ----------------------------------------------------

        html.Div(
            [

                html.H2(
                    "Engagement Analysis"
                ),

                html.P(
                    "Relationship between likes, retweets, replies and sentiment.",
                    style={
                        "color": "#666"
                    }
                ),

                dcc.Graph(
                    id="user-comment-insights"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),


        # ----------------------------------------------------
        # TOP AUTHORS / ACCOUNTS
        # ----------------------------------------------------

        html.Div(
            [
                html.H2(
                    "Top Authors by Engagement"
                ),

                html.P(
                    "Accounts whose posts generated the highest combined likes, retweets and replies.",
                    style={
                        "color": "#666"
                    }
                ),

                dcc.Graph(
                    id="top-authors-chart"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),


        # ----------------------------------------------------
        # ENGAGEMENT SHARE / RATE ANALYSIS
        # ----------------------------------------------------

        html.Div(
            [
                html.H2(
                    "Engagement Rate / Share Analysis"
                ),

                html.P(
                    "Engagement is calculated from likes + retweets + replies. "
                    "Because follower counts are not available in the current live X data, "
                    "this dashboard uses engagement share and average engagement per post "
                    "instead of a follower-based engagement rate.",
                    style={
                        "color": "#666"
                    }
                ),

                dcc.Graph(
                    id="engagement-rate-chart"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),


        # ----------------------------------------------------
        # POPULAR COMMENTS
        # ----------------------------------------------------

        html.Div(
            [

                html.H2(
                    "Most Popular Comments"
                ),

                html.P(
                    "Top five comments ranked by likes.",
                    style={
                        "color": "#666"
                    }
                ),

                dcc.Graph(
                    id="Top-Tweets-Insights"
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "25px",
                "borderRadius": "15px",
                "margin": "20px 40px 40px 40px",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)"
            }
        ),



        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        html.Div(
            "Social Media Sentiment Analytics • Data Analyst Portfolio Project",
            style={
                "textAlign": "center",
                "color": "#888",
                "fontSize": "13px",
                "padding": "10px 0 25px 0"
            }
        ),

        # Retained for compatibility with the original project.
        dcc.Input(id="input-url", type="text", value="", style={"display": "none"})

    ],

    style={
        "backgroundColor": "#f5f7fb",
        "minHeight": "100vh",
        "fontFamily": "Arial, sans-serif",
        "paddingBottom": "30px"
    }
)


# ============================================================
# DASH CALLBACK
# ============================================================

@dash_app.callback(

    Output(
        "kpi-container",
        "children"
    ),

    Output(
        "sentiment-distribution-chart",
        "figure"
    ),

    Output(
        "sentiment-time-series-chart",
        "figure"
    ),

    Output(
        "user-comment-insights",
        "figure"
    ),

    Output(
        "Top-Tweets-Insights",
        "figure"
    ),

    Output(
        "top-authors-chart",
        "figure"
    ),

    Output(
        "engagement-rate-chart",
        "figure"
    ),

    Output(
        "data-source-status",
        "children"
    ),

    Output(
        "live-error",
        "children"
    ),

    Input(
        "x-search",
        "value"
    ),

    Input(
        "sentiment-filter",
        "value"
    ),

    Input(
        "minimum-likes",
        "value"
    )
)


def update_insights(search_query, selected_sentiment, minimum_likes):

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    try:
        df, small_df = get_data(search_query)
        live_mode = bool(search_query and search_query.strip())
        source_status = (
            f"Live X data: {len(df)} posts returned for \"{search_query.strip()}\"."
            if live_mode
            else "Using the local collected_data.csv dataset."
        )
        live_error = ""
    except XAPIError as exc:
        # Do not fabricate results when live X access is unavailable.
        empty = go.Figure()
        empty.update_layout(
            title="Live X data unavailable",
            annotations=[{
                "text": str(exc),
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False
            }]
        )
        empty_kpis = [html.Div("Live X search unavailable. Configure XFETCH_API_KEY.", style={"padding": "20px", "fontWeight": "600"})]
        return (
            empty_kpis,
            empty,
            empty,
            empty,
            empty,
            empty,
            empty,
            "Live X search is selected.",
            str(exc)
        )

    df = df.copy()


    # --------------------------------------------------------
    # BASIC CLEANING
    # --------------------------------------------------------

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        errors="coerce"
    )

    df["sentiments"] = pd.to_numeric(
        df["sentiments"],
        errors="coerce"
    )

    df["comment_likes"] = pd.to_numeric(
        df["comment_likes"],
        errors="coerce"
    ).fillna(0)

    df["comment_retweets"] = pd.to_numeric(
        df["comment_retweets"],
        errors="coerce"
    ).fillna(0)

    df["comment_replies"] = pd.to_numeric(
        df["comment_replies"],
        errors="coerce"
    ).fillna(0)

    df = df.dropna(
        subset=["sentiments"]
    )

    # --------------------------------------------------------
    # ENGAGEMENT METRICS
    # --------------------------------------------------------
    # This is an observable engagement metric based on the fields
    # available from the live X/xFetch response.
    df["total_engagement"] = (
        df["comment_likes"]
        + df["comment_retweets"]
        + df["comment_replies"]
    )


    # --------------------------------------------------------
    # SENTIMENT CATEGORIES
    # --------------------------------------------------------

    def sentiment_category(score):

        if score >= 0.525:
            return "Positive"

        elif score <= 0.475:
            return "Negative"

        else:
            return "Neutral"


    df["sentiment_category"] = df[
        "sentiments"
    ].apply(sentiment_category)


    # --------------------------------------------------------
    # INTERACTIVE FILTERS
    # --------------------------------------------------------

    if selected_sentiment and selected_sentiment != "All":
        df = df[
            df["sentiment_category"] == selected_sentiment
        ].copy()

    try:
        minimum_likes = float(minimum_likes or 0)
    except (TypeError, ValueError):
        minimum_likes = 0

    df = df[
        df["comment_likes"] >= minimum_likes
    ].copy()


    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    total_comments = len(df)

    positive_count = len(
        df[
            df["sentiment_category"] == "Positive"
        ]
    )

    neutral_count = len(
        df[
            df["sentiment_category"] == "Neutral"
        ]
    )

    negative_count = len(
        df[
            df["sentiment_category"] == "Negative"
        ]
    )


    if total_comments > 0:

        positive_percentage = round(
            positive_count / total_comments * 100,
            1
        )

        neutral_percentage = round(
            neutral_count / total_comments * 100,
            1
        )

        negative_percentage = round(
            negative_count / total_comments * 100,
            1
        )

    else:

        positive_percentage = 0
        neutral_percentage = 0
        negative_percentage = 0


    total_likes = int(
        df["comment_likes"].sum()
    )

    total_retweets = int(
        df["comment_retweets"].sum()
    )

    total_replies = int(
        df["comment_replies"].sum()
    )

    total_engagement = int(
        df["total_engagement"].sum()
    )

    average_engagement = (
        round(total_engagement / total_comments, 2)
        if total_comments > 0
        else 0
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    def create_kpi_card(
        title,
        value,
        subtitle
    ):

        return html.Div(

            [

                html.P(
                    title,
                    style={
                        "margin": "0",
                        "fontSize": "14px",
                        "fontWeight": "600",
                        "color": "#666"
                    }
                ),

                html.H2(
                    value,
                    style={
                        "margin": "8px 0 4px 0",
                        "fontSize": "28px"
                    }
                ),

                html.P(
                    subtitle,
                    style={
                        "margin": "0",
                        "fontSize": "12px",
                        "color": "#888"
                    }
                )

            ],

            style={
                "backgroundColor": "white",
                "padding": "18px 10px",
                "borderRadius": "15px",
                "minWidth": "0",
                "flex": "1 1 130px",
                "textAlign": "center",
                "boxShadow": "0 4px 15px rgba(0,0,0,0.08)",
                "overflow": "hidden"
            }
        )


    kpis = [

        create_kpi_card(
            "TOTAL COMMENTS",
            str(total_comments),
            "User responses"
        ),

        create_kpi_card(
            "POSITIVE",
            f"{positive_percentage}%",
            f"{positive_count} comments"
        ),

        create_kpi_card(
            "NEUTRAL",
            f"{neutral_percentage}%",
            f"{neutral_count} comments"
        ),

        create_kpi_card(
            "NEGATIVE",
            f"{negative_percentage}%",
            f"{negative_count} comments"
        ),

        create_kpi_card(
            "TOTAL LIKES",
            f"{total_likes:,}",
            "Across all comments"
        ),

        create_kpi_card(
            "TOTAL RETWEETS",
            f"{total_retweets:,}",
            "Across all comments"
        ),

        create_kpi_card(
            "TOTAL ENGAGEMENT",
            f"{total_engagement:,}",
            "Likes + retweets + replies"
        ),

        create_kpi_card(
            "AVG ENGAGEMENT",
            f"{average_engagement:,.2f}",
            "Per returned post"
        )

    ]


    # ========================================================
    # SENTIMENT DISTRIBUTION
    # ========================================================

    if df.empty:
        sentiment_counts = pd.DataFrame({
            "sentiment": ["No Data"],
            "count": [0]
        })
    else:
        sentiment_counts = (
        df["sentiment_category"]
            .value_counts()
            .reset_index()
        )

    sentiment_counts.columns = [
        "sentiment",
        "count"
    ]


    fig_sentiment_distribution = px.bar(

        sentiment_counts,

        x="sentiment",

        y="count",

        text="count",

        title="Positive vs Neutral vs Negative Comments",

        labels={
            "sentiment": "Sentiment",
            "count": "Number of Comments"
        }
    )


    fig_sentiment_distribution.update_layout(

        plot_bgcolor="white",

        paper_bgcolor="white",

        title_x=0.5,

        hovermode="x unified",
        margin=dict(l=50, r=30, t=70, b=50)
    )


    # ========================================================
    # SENTIMENT OVER TIME
    # ========================================================

    fig1 = go.Figure(

        data=[

            go.Scatter(

                x=df["datetime"],

                y=df["sentiments"],

                mode="markers",

                marker=dict(
                    size=10,
                    color=df["sentiments"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(
                        title="Sentiment"
                    )
                ),

                text=df["comment"],

                hovertemplate=
                "<b>%{text}</b>"
                "<br>Sentiment: %{y:.3f}"
                "<br>Date: %{x}"
                "<extra></extra>"

            )

        ]

    )


    fig1.update_layout(

        title="Sentiment Score Over Time",

        title_x=0.5,

        xaxis=dict(
            title="Date & Time",
            gridcolor="#eeeeee"
        ),

        yaxis=dict(
            title="Sentiment Score",
            range=[0, 1],
            gridcolor="#eeeeee"
        ),

        plot_bgcolor="white",

        paper_bgcolor="white",
        margin=dict(l=50, r=30, t=70, b=50)
    )


    # ========================================================
    # ENGAGEMENT ANALYSIS
    # ========================================================

    fig2 = px.scatter(

        df,

        x="comment_likes",

        y="comment_retweets",

        size="comment_replies",

        color="sentiments",

        hover_name="comment",

        hover_data=[
            "username",
            "comment_likes",
            "comment_retweets",
            "comment_replies",
            "sentiment_category"
        ],

        color_continuous_scale="Viridis",

        log_x=True,

        title="Engagement: Likes vs Retweets"
    )


    fig2.update_layout(

        title_x=0.5,

        xaxis_title="Comment Likes",

        yaxis_title="Comment Retweets",

        plot_bgcolor="#f4f4f4",

        paper_bgcolor="white"
    )


    # ========================================================
    # ENGAGEMENT RATE / SHARE ANALYSIS
    # ========================================================

    if not df.empty:
        engagement_df = df.copy()

        engagement_total = engagement_df["total_engagement"].sum()

        if engagement_total > 0:
            engagement_df["engagement_share_pct"] = (
                engagement_df["total_engagement"]
                / engagement_total
                * 100
            )
        else:
            engagement_df["engagement_share_pct"] = 0

        engagement_df = (
            engagement_df
            .sort_values(
                "total_engagement",
                ascending=False
            )
            .head(10)
            .copy()
        )

        engagement_df["post_label"] = (
            engagement_df["username"]
            .fillna("Unknown")
            .astype(str)
            + " • "
            + engagement_df["comment"].fillna("").astype(str).str.slice(0, 45)
        )

    else:
        engagement_df = pd.DataFrame({
            "post_label": ["No Data"],
            "total_engagement": [0],
            "engagement_share_pct": [0],
            "comment_likes": [0],
            "comment_retweets": [0],
            "comment_replies": [0]
        })

    fig_engagement_rate = px.bar(
        engagement_df.sort_values(
            "total_engagement",
            ascending=True
        ),
        x="total_engagement",
        y="post_label",
        orientation="h",
        text="total_engagement",
        hover_data={
            "total_engagement": True,
            "engagement_share_pct": ":.2f",
            "comment_likes": True,
            "comment_retweets": True,
            "comment_replies": True,
            "post_label": False
        },
        title="Top Posts by Observable Engagement",
        labels={
            "total_engagement": "Total Engagement",
            "post_label": "Post"
        }
    )

    fig_engagement_rate.update_traces(
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Total Engagement: %{x:,}"
            "<br>Engagement Share: %{customdata[0]:.2f}%"
            "<br>Likes: %{customdata[1]:,}"
            "<br>Retweets: %{customdata[2]:,}"
            "<br>Replies: %{customdata[3]:,}"
            "<extra></extra>"
        )
    )

    fig_engagement_rate.update_layout(
        title_x=0.5,
        xaxis_title="Likes + Retweets + Replies",
        yaxis_title="Post",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=30, t=70, b=50)
    )


    # ========================================================
    # POPULAR COMMENTS TABLE
    # ========================================================

    top_comments = (
        df.sort_values(
            "comment_likes",
            ascending=False
        )
        .head(5)
    )

    if len(top_comments) > 0:
        table_comments = top_comments["comment"].fillna("")
        table_likes = top_comments["comment_likes"]
        table_sentiments = top_comments["sentiments"]
    else:
        table_comments = pd.Series(["No matching comments"])
        table_likes = pd.Series([0])
        table_sentiments = pd.Series([0])


    # ========================================================
    # TOP AUTHORS / ACCOUNTS
    # ========================================================

    if not df.empty:
        author_df = df.copy()

        author_df["engagement"] = author_df["total_engagement"]

        top_authors = (
            author_df
            .groupby("username", dropna=False)
            .agg(
                posts=("comment", "count"),
                likes=("comment_likes", "sum"),
                retweets=("comment_retweets", "sum"),
                replies=("comment_replies", "sum"),
                engagement=("engagement", "sum")
            )
            .reset_index()
            .sort_values("engagement", ascending=False)
            .head(10)
        )

        top_authors["username"] = (
            top_authors["username"]
            .fillna("Unknown")
            .astype(str)
        )

    else:
        top_authors = pd.DataFrame({
            "username": ["No Data"],
            "posts": [0],
            "likes": [0],
            "retweets": [0],
            "replies": [0],
            "engagement": [0]
        })

    fig_authors = px.bar(
        top_authors.sort_values("engagement", ascending=True),
        x="engagement",
        y="username",
        orientation="h",
        text="engagement",
        hover_data=[
            "posts",
            "likes",
            "retweets",
            "replies"
        ],
        title="Top 10 Authors by Total Engagement"
    )

    fig_authors.update_layout(
        title_x=0.5,
        xaxis_title="Total Engagement",
        yaxis_title="Author",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=30, t=70, b=50)
    )


    # --------------------------------------------------------
    # TABLE COLORS
    # --------------------------------------------------------

    row_colors = [
        "#E8F0FE",
        "#DCEBFA",
        "#D0E3F5",
        "#C4DCF0",
        "#B8D5EC"
    ][:len(table_comments)]


    fig3 = go.Figure(

        data=[

            go.Table(

                header=dict(

                    values=[
                        "Comment",
                        "Likes",
                        "Sentiment Score"
                    ],

                    fill_color="#667eea",

                    font=dict(
                        color="white",
                        size=13
                    ),

                    align="center"
                ),

                cells=dict(

                    values=[
                        table_comments,
                        table_likes,
                        table_sentiments
                    ],

                    fill_color=[
                        row_colors
                    ],

                    font=dict(
                        color="#222",
                        size=12
                    ),

                    align="left",

                    height=45

                )

            )

        ]

    )


    fig3.update_layout(

        title="Top 5 Most Popular Comments",

        title_x=0.5,

        paper_bgcolor="white"
    )


    # ========================================================
    # RETURN ALL DASHBOARD COMPONENTS
    # ========================================================

    return (
        kpis,
        fig_sentiment_distribution,
        fig1,
        fig2,
        fig3,
        fig_authors,
        fig_engagement_rate,
        source_status,
        live_error
    )


# ============================================================
# FLASK ROUTES
# ============================================================

@server.route("/")
def index():

    return render_template(
        "index.html"
    )


@server.route(
    "/",
    methods=["GET", "POST"]
)
def hello():

    if request.method == "POST":

        url = request.form.get(
            "Tweet_URL"
        )

        session["url"] = url

    return redirect(
        url_for("dashboard")
    )


@server.route("/dashboard/")
def dashboard():

    return redirect(
        "/dash"
    )


# ============================================================
# DISPATCHER
# ============================================================

app = DispatcherMiddleware(

    server,

    {
        "/dash": dash_app.server
    }

)


# ============================================================
# RUN APPLICATION
# ============================================================

run_simple(

    "0.0.0.0",

    8080,

    app,

    use_reloader=True,

    use_debugger=True
)