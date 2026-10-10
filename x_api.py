import requests
import pandas as pd

from get_sentimet import generate_sentiments

BASE_URL = "https://api.xfetch.io/v1/search/recent"


class XAPIError(Exception):
    """Raised when the xfetch live X search cannot be completed."""
    pass


def _normalize_query(query):
    query = str(query).strip()
    if not query:
        raise XAPIError("Enter an X search term.")

    # Convenience: @handle becomes a valid X-style account search.
    if query.startswith("@") and " " not in query:
        query = f"from:{query[1:]}"

    return query


def search_recent_posts(query, api_key, max_results=20):
    """
    Search current public X posts through xfetch.

    xfetch documents /v1/search/recent as a GET endpoint using
    Authorization: Bearer <XFETCH_API_KEY>.
    """
    query = _normalize_query(query)
    api_key = str(api_key or "").strip()
    if not api_key:
        raise XAPIError("XFETCH_API_KEY is not configured.")

    params = {
        "query": query,
        "limit": min(max(int(max_results), 1), 20),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise XAPIError(f"Could not connect to xfetch: {exc}") from exc

    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise XAPIError(
            f"xfetch returned HTTP {response.status_code}: {detail}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise XAPIError("xfetch returned invalid JSON.") from exc

    posts = payload.get("data", []) or []

    rows = []
    for post in posts:
        rows.append({
            "id": post.get("id"),
            "username": post.get("username") or post.get("author_username") or post.get("author_id", "unknown"),
            "datetime": post.get("created_at"),
            "comment": post.get("text", ""),
            "comment_replies": post.get("reply_count", 0) or 0,
            "comment_retweets": post.get("retweet_count", 0) or 0,
            "comment_likes": post.get("like_count", 0) or 0,
        })

    columns = [
        "id", "username", "datetime", "comment",
        "comment_replies", "comment_retweets", "comment_likes"
    ]
    df = pd.DataFrame(rows, columns=columns)

    if not df.empty:
        for col in ["comment_replies", "comment_retweets", "comment_likes"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df["sentiments"] = generate_sentiments(df)
    else:
        df["sentiments"] = pd.Series(dtype=float)

    small_data = (
        df.sort_values("comment_likes", ascending=False).head(5)[
            ["comment", "comment_likes", "sentiments"]
        ]
        .rename(columns={
            "comment": "Comment",
            "comment_likes": "Comment Likes",
            "sentiments": "Comment Sentiment Score"
        })
    )

    return df, small_data
