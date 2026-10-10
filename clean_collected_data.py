import os
import pandas as pd

from get_sentimet import generate_sentiments


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_DATA_FILE = "./collected_data.csv"


# ============================================================
# NUMBER CONVERSION
# ============================================================

def convert_str(col):
    """
    Convert social-media engagement values such as:

    7.7K  -> 7700
    2.5M  -> 2500000
    1.2B  -> 1200000000
    1,250 -> 1250
    """

    col = col.astype(str).str.strip()

    # Remove commas
    col = col.str.replace(",", "", regex=False)

    # Convert K
    col = col.str.replace(
        r"^\s*([0-9]*\.?[0-9]+)\s*[Kk]\s*$",
        lambda m: str(float(m.group(1)) * 1_000),
        regex=True
    )

    # Convert M
    col = col.str.replace(
        r"^\s*([0-9]*\.?[0-9]+)\s*[Mm]\s*$",
        lambda m: str(float(m.group(1)) * 1_000_000),
        regex=True
    )

    # Convert B
    col = col.str.replace(
        r"^\s*([0-9]*\.?[0-9]+)\s*[Bb]\s*$",
        lambda m: str(float(m.group(1)) * 1_000_000_000),
        regex=True
    )

    return pd.to_numeric(
        col,
        errors="coerce"
    ).fillna(0)


# ============================================================
# LOAD DATA
# ============================================================

def load_data(file_path=None):
    """
    Load an X/Twitter dataset.

    If no file is supplied, the original collected_data.csv
    is used.
    """

    if file_path is None:
        file_path = os.environ.get(
            "SOCIAL_DATA_FILE",
            DEFAULT_DATA_FILE
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    data = pd.read_csv(
        file_path
    )

    return data


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_columns(data):

    required_columns = [
        "username",
        "datetime",
        "comment",
        "comment_replies",
        "comment_retweets",
        "comment_likes"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


# ============================================================
# PREPROCESS DATA
# ============================================================

def preprocess_data(file_path=None):

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    data = load_data(
        file_path
    )

    data = data.copy()


    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validate_columns(
        data
    )


    # --------------------------------------------------------
    # REMOVE COMPLETELY EMPTY COMMENTS
    # --------------------------------------------------------

    data["comment"] = (
        data["comment"]
        .astype(str)
        .str.strip()
    )

    data = data[
        (data["comment"] != "")
        &
        (data["comment"].str.lower() != "nan")
    ].copy()


    # --------------------------------------------------------
    # DATETIME
    # --------------------------------------------------------

    data["datetime"] = pd.to_datetime(
        data["datetime"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # ENGAGEMENT METRICS
    # --------------------------------------------------------

    engagement_columns = [
        "comment_likes",
        "comment_retweets",
        "comment_replies"
    ]

    for column in engagement_columns:

        data[column] = convert_str(
            data[column]
        )


    # --------------------------------------------------------
    # SENTIMENT ANALYSIS
    # --------------------------------------------------------

    if len(data) > 0:

        data["sentiments"] = generate_sentiments(
            data
        )

    else:

        data["sentiments"] = []


    # --------------------------------------------------------
    # SMALL DATASET FOR TABLE
    # --------------------------------------------------------

    top_data = (
        data
        .sort_values(
            "comment_likes",
            ascending=False
        )
        .head(5)
    )

    small_data = pd.DataFrame({

        "Comment": top_data[
            "comment"
        ].tolist(),

        "Comment Likes": top_data[
            "comment_likes"
        ].tolist(),

        "Comment Sentiment Score": top_data[
            "sentiments"
        ].tolist()

    })


    return data, small_data


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    data, small_data = preprocess_data()

    print("\n======================================")
    print("DATASET LOADED SUCCESSFULLY")
    print("======================================")

    print(
        f"Total comments: {len(data)}"
    )

    print(
        f"Total likes: {data['comment_likes'].sum():,.0f}"
    )

    print(
        f"Total retweets: {data['comment_retweets'].sum():,.0f}"
    )

    print(
        f"Total replies: {data['comment_replies'].sum():,.0f}"
    )

    print("\nTop comments:")

    print(
        small_data.to_string(
            index=False
        )
    )