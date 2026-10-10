# 📊 Social Media Analytics & Sentiment Analysis

An interactive data analytics project designed to analyze social media conversations, understand audience sentiment, measure engagement, and uncover meaningful insights through Python applications and Power BI dashboards.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?logo=flask&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20App-FF4B4B?logo=streamlit&logoColor=white)

---

## 📌 Overview

Social media platforms generate large volumes of user-generated content. Analyzing this content can help identify audience opinions, understand engagement patterns, and discover which topics attract the most attention.

This project combines sentiment analysis, data processing, and interactive visualization to explore social media posts and transform raw data into actionable analytical insights.

The project includes a web-based sentiment analysis application and a Power BI dashboard for exploring social media performance.

## 🎯 Objectives

- Analyze social media post text and sentiment.
- Classify posts into positive, neutral, and negative categories.
- Measure likes, retweets, replies, and total engagement.
- Identify high-performing topics and posts.
- Compare engagement across sentiment categories.
- Explore changes in posting activity and engagement over time.
- Present findings through interactive charts and dashboards.

## ✨ Key Features

### 🧠 Sentiment Analysis
- Analyze text and calculate sentiment scores.
- Categorize posts as positive, neutral, or negative.
- Explore sentiment patterns across topics.

### 📈 Engagement Analytics
- Analyze likes, retweets, and replies.
- Compare total and average engagement.
- Identify top-performing posts and users.
- Explore relationships between likes and retweets.

### 📊 Interactive Power BI Dashboard
- Sentiment distribution analysis.
- Engagement by topic and sentiment.
- Post volume and engagement trends.
- Average engagement by day of the week.
- Top users and posts by engagement.
- Interactive visual comparisons.

### 🔎 Data Processing
- Handle and transform social media datasets.
- Clean missing and inconsistent values.
- Process dates and numerical engagement metrics.
- Prepare analytical features for visualization.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and analysis |
| Pandas | Data manipulation and cleaning |
| VADER Sentiment | Text sentiment scoring |
| Flask | Web application backend |
| Streamlit | Interactive application interface |
| Plotly and Dash | Interactive visualizations |
| Power BI | Business intelligence and dashboarding |
| MySQL | Relational data storage and SQL analytics |
| Git and GitHub | Version control and project hosting |

*The repository includes multiple application components; not every technology is necessarily used by every component.*

## 📊 Dashboard Insights

The Power BI dashboard supports analysis of the following metrics:

| Analysis | Purpose |
|---|---|
| Sentiment Distribution | Understand the share of positive, neutral, and negative posts |
| Engagement by Topic | Compare engagement across different topics |
| Engagement Over Time | Identify trends in engagement |
| Top Users by Engagement | Find users whose posts generate the most engagement |
| Average Likes by Sentiment | Compare likes across sentiment categories |
| Posts by Topic | Understand content distribution |
| Likes vs. Retweets | Explore relationships between engagement metrics |
| Sentiment by Topic | Compare sentiment patterns across topics |
| Engagement by Weekday | Examine differences across days of the week |
| Post Volume vs. Average Engagement | Compare content volume with average performance |

## 📁 Project Structure

```text
Social_Media_Analytics/
│
├── app.py
├── Streamlit_app.py
├── x_api.py
├── get_sentimet.py
├── clean_collected_data.py
├── requirements.txt
├── .gitignore
│
├── collected_data.csv
├── social_media_analytics_25000.csv
├── SOCIAL_MEDIA_INSIGHTS1.pbix
│
├── templates/
│   └── index.html
│
├── static/
│   ├── styles/
│   │   └── styles.css
│   ├── Twitter.jpg
│   └── example.gif
│
└── README.md
```

*This is an example structure. Adjust it to match the files actually included in the repository. Keep API keys and virtual environment files out of GitHub.*

## ⚙️ Installation and Setup

### Prerequisites

- Python installed on your system
- Git
- Power BI Desktop for the `.pbix` dashboard
- An API key if you want to use the configured live-search integration

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd Social_Media_Analytics
```

Replace `YOUR_REPOSITORY_URL` with the URL of your GitHub repository.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Use compatible dependency versions for your Python installation. Older project dependencies may require updates before installation.

### 4. Configure environment variables

For the optional xfetch live-search integration, create a local `.env` file:

```env
XFETCH_API_KEY=your_api_key_here
```

Never commit the actual API key to GitHub.

### 5. Run the Flask/Dash application

```bash
python app.py
```

Open the local URL displayed in the terminal.

### 6. Run the Streamlit application

```bash
python -m streamlit run Streamlit_app.py
```

Open the local URL displayed by Streamlit, usually:

`http://localhost:8501`

### 7. Open the Power BI dashboard

Open `SOCIAL_MEDIA_INSIGHTS1.pbix` in Power BI Desktop.

## 📂 Dataset

The project supports social media post datasets containing fields such as:

- Post ID
- Username
- Date and time
- Post text
- Topic
- Likes, retweets, and replies
- Sentiment score and category
- Total engagement

A 25,000-row synthetic dataset is available for practice, exploratory analysis, and dashboard development.

**Data note:** Synthetic data is for demonstration and practice. It should not be interpreted as real social media activity. Live-search results depend on the configured third-party service and its availability.

## 🔬 Analytical Workflow

1. **Data collection:** Load CSV data or retrieve posts through the configured API.
2. **Data cleaning:** Process missing values, dates, text, and engagement metrics.
3. **Sentiment analysis:** Estimate the sentiment polarity of post text.
4. **Feature engineering:** Prepare engagement and text-related metrics.
5. **Exploratory data analysis:** Compare topics, sentiment, and engagement.
6. **Visualization:** Build charts and interactive Power BI reports.
7. **Insight generation:** Identify patterns that can inform content strategy.

## 💼 Business Applications

The analytical techniques demonstrated in this project can support:

- Social media performance monitoring
- Brand sentiment exploration
- Audience opinion analysis
- Content performance evaluation
- Topic and trend analysis
- Data-driven marketing decisions

## 🚀 Future Improvements

- Automated data refresh
- More advanced sentiment classification
- Topic modelling and keyword extraction
- Improved handling of sarcasm and contextual language
- Database integration and historical trend analysis
- Deployment of interactive dashboards
- Additional business intelligence metrics

## 🔐 Security and Data Usage

- Keep API keys and credentials private.
- Exclude `.env` and `.venv/` from version control.
- Respect the terms and rate limits of the data provider.
- Clearly distinguish synthetic datasets from real collected data.

## 📄 License

No license is specified by default. Add a `LICENSE` file if you intend to define permissions for reuse, modification, or distribution.

---

**Built with Python, sentiment analysis, and business intelligence tools.**