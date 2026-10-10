CREATE DATABASE customer_review_analytics;

USE customer_review_analytics;
SELECT DATABASE();
CREATE TABLE posts (
    id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(255),
    datetime DATETIME,
    comment TEXT,
    comment_replies INT DEFAULT 0,
    comment_retweets INT DEFAULT 0,
    comment_likes INT DEFAULT 0,
    sentiment_score DECIMAL(10,6),
    sentiment_category VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
DESCRIBE posts;

CREATE INDEX idx_username
ON posts(username);

CREATE INDEX idx_datetime
ON posts(datetime);

CREATE INDEX idx_sentiment_category
ON posts(sentiment_category);

CREATE INDEX idx_likes
ON posts(comment_likes);

CREATE INDEX idx_retweets
ON posts(comment_retweets);
CREATE OR REPLACE VIEW post_engagement_analysis AS
SELECT
    id,
    username,
    datetime,
    comment,
    comment_likes,
    comment_retweets,
    comment_replies,
    sentiment_score,
    sentiment_category,
    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement
FROM posts;

SELECT *
FROM post_engagement_analysis
LIMIT 10;

CREATE OR REPLACE VIEW engagement_summary AS
SELECT
    COUNT(*) AS total_posts,
    SUM(comment_likes) AS total_likes,
    SUM(comment_retweets) AS total_retweets,
    SUM(comment_replies) AS total_replies,
    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,
    ROUND(
        AVG(
            comment_likes
            + comment_retweets
            + comment_replies
        ), 2
    ) AS average_engagement
FROM posts;

SELECT *
FROM engagement_summary;
USE customer_review_analytics;

CREATE INDEX idx_username
ON posts(username);

CREATE INDEX idx_datetime
ON posts(datetime);

CREATE INDEX idx_sentiment_category
ON posts(sentiment_category);

CREATE INDEX idx_likes
ON posts(comment_likes);

CREATE INDEX idx_retweets
ON posts(comment_retweets);

SHOW INDEX FROM posts;

USE customer_review_analytics;

CREATE OR REPLACE VIEW post_engagement_analysis AS
SELECT
    id,
    username,
    datetime,
    comment,
    comment_likes,
    comment_retweets,
    comment_replies,
    sentiment_score,
    sentiment_category,
    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement
FROM posts;

SELECT *
FROM post_engagement_analysis
LIMIT 10;

CREATE OR REPLACE VIEW engagement_summary AS
SELECT
    COUNT(*) AS total_posts,
    COALESCE(SUM(comment_likes), 0) AS total_likes,
    COALESCE(SUM(comment_retweets), 0) AS total_retweets,
    COALESCE(SUM(comment_replies), 0) AS total_replies,
    COALESCE(
        SUM(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        0
    ) AS total_engagement,
    COALESCE(
        ROUND(
            AVG(
                comment_likes
                + comment_retweets
                + comment_replies
            ),
            2
        ),
        0
    ) AS average_engagement
FROM posts;
SELECT *
FROM engagement_summary;

USE customer_review_analytics;

CREATE OR REPLACE VIEW author_engagement_analysis AS
SELECT
    username,
    COUNT(*) AS total_posts,
    COALESCE(SUM(comment_likes), 0) AS total_likes,
    COALESCE(SUM(comment_retweets), 0) AS total_retweets,
    COALESCE(SUM(comment_replies), 0) AS total_replies,

    COALESCE(
        SUM(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        0
    ) AS total_engagement,

    COALESCE(
        ROUND(
            AVG(
                comment_likes
                + comment_retweets
                + comment_replies
            ),
            2
        ),
        0
    ) AS average_engagement_per_post

FROM posts

GROUP BY username;
USE customer_review_analytics;

CREATE OR REPLACE VIEW sentiment_analysis AS
SELECT
    COUNT(*) AS total_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Positive' THEN 1
            ELSE 0
        END
    ) AS positive_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Neutral' THEN 1
            ELSE 0
        END
    ) AS neutral_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Negative' THEN 1
            ELSE 0
        END
    ) AS negative_posts,

    ROUND(
        SUM(
            CASE
                WHEN sentiment_category = 'Positive' THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS positive_percentage,

    ROUND(
        SUM(
            CASE
                WHEN sentiment_category = 'Neutral' THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS neutral_percentage,

    ROUND(
        SUM(
            CASE
                WHEN sentiment_category = 'Negative' THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS negative_percentage

FROM posts;

CREATE OR REPLACE VIEW author_sentiment_analysis AS
SELECT
    username,

    COUNT(*) AS total_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Positive' THEN 1
            ELSE 0
        END
    ) AS positive_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Neutral' THEN 1
            ELSE 0
        END
    ) AS neutral_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Negative' THEN 1
            ELSE 0
        END
    ) AS negative_posts,

    ROUND(AVG(sentiment_score), 4) AS average_sentiment_score

FROM posts

GROUP BY username;

CREATE OR REPLACE VIEW sentiment_over_time AS
SELECT
    DATE(datetime) AS analysis_date,

    COUNT(*) AS total_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Positive' THEN 1
            ELSE 0
        END
    ) AS positive_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Neutral' THEN 1
            ELSE 0
        END
    ) AS neutral_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Negative' THEN 1
            ELSE 0
        END
    ) AS negative_posts,

    ROUND(
        AVG(sentiment_score),
        4
    ) AS average_sentiment_score,

    SUM(comment_likes) AS total_likes,

    SUM(comment_retweets) AS total_retweets,

    SUM(comment_replies) AS total_replies,

    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement

FROM posts

WHERE datetime IS NOT NULL

GROUP BY DATE(datetime)

ORDER BY analysis_date;


-- ============================================================
-- 8. DAILY ENGAGEMENT ANALYSIS
-- ============================================================

CREATE OR REPLACE VIEW daily_engagement_analysis AS
SELECT
    DATE(datetime) AS analysis_date,

    COUNT(*) AS total_posts,

    SUM(comment_likes) AS total_likes,

    SUM(comment_retweets) AS total_retweets,

    SUM(comment_replies) AS total_replies,

    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    ROUND(
        AVG(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        2
    ) AS average_engagement

FROM posts

WHERE datetime IS NOT NULL

GROUP BY DATE(datetime)

ORDER BY analysis_date;


-- ============================================================
-- 9. TOP POSTS BY ENGAGEMENT
-- ============================================================

CREATE OR REPLACE VIEW top_posts_by_engagement AS
SELECT
    id,
    username,
    datetime,
    comment,

    comment_likes,

    comment_retweets,

    comment_replies,

    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    sentiment_score,

    sentiment_category

FROM posts

ORDER BY total_engagement DESC;


-- ============================================================
-- 10. TOP POSTS BY LIKES
-- ============================================================

CREATE OR REPLACE VIEW top_posts_by_likes AS
SELECT
    id,
    username,
    datetime,
    comment,

    comment_likes,

    comment_retweets,

    comment_replies,

    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    sentiment_score,

    sentiment_category

FROM posts

ORDER BY comment_likes DESC;


-- ============================================================
-- 11. TOP POSTS BY RETWEETS
-- ============================================================

CREATE OR REPLACE VIEW top_posts_by_retweets AS
SELECT
    id,
    username,
    datetime,
    comment,

    comment_retweets,

    comment_likes,

    comment_replies,

    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    sentiment_score,

    sentiment_category

FROM posts

ORDER BY comment_retweets DESC;


-- ============================================================
-- 12. TOP AUTHORS
-- ============================================================

CREATE OR REPLACE VIEW top_authors AS
SELECT
    username,

    COUNT(*) AS total_posts,

    SUM(comment_likes) AS total_likes,

    SUM(comment_retweets) AS total_retweets,

    SUM(comment_replies) AS total_replies,

    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    ROUND(
        AVG(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        2
    ) AS average_engagement,

    ROUND(
        AVG(sentiment_score),
        4
    ) AS average_sentiment

FROM posts

GROUP BY username

ORDER BY total_engagement DESC;


-- ============================================================
-- 13. AUTHOR SENTIMENT ANALYSIS
-- ============================================================

CREATE OR REPLACE VIEW author_sentiment_analysis AS
SELECT
    username,

    COUNT(*) AS total_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Positive' THEN 1
            ELSE 0
        END
    ) AS positive_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Neutral' THEN 1
            ELSE 0
        END
    ) AS neutral_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Negative' THEN 1
            ELSE 0
        END
    ) AS negative_posts,

    ROUND(
        AVG(sentiment_score),
        4
    ) AS average_sentiment_score

FROM posts

GROUP BY username

ORDER BY average_sentiment_score DESC;


-- ============================================================
-- 14. ENGAGEMENT SHARE ANALYSIS
-- ============================================================
-- NOTE:
-- This is an engagement-share metric based on the posts
-- returned by the system.
-- It is NOT a follower-based social-media engagement rate.

CREATE OR REPLACE VIEW engagement_share_analysis AS
SELECT
    id,
    username,
    datetime,
    comment,

    comment_likes,

    comment_retweets,

    comment_replies,

    (
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    ROUND(
        (
            comment_likes
            + comment_retweets
            + comment_replies
        )
        * 100.0
        /
        NULLIF(
            (
                SELECT SUM(
                    p2.comment_likes
                    + p2.comment_retweets
                    + p2.comment_replies
                )
                FROM posts p2
            ),
            0
        ),
        2
    ) AS engagement_share_percentage,

    sentiment_score,

    sentiment_category

FROM posts

ORDER BY engagement_share_percentage DESC;


-- ============================================================
-- 15. MONTHLY ANALYTICS
-- ============================================================

CREATE OR REPLACE VIEW monthly_analytics AS
SELECT
    DATE_FORMAT(datetime, '%Y-%m') AS analysis_month,

    COUNT(*) AS total_posts,

    SUM(comment_likes) AS total_likes,

    SUM(comment_retweets) AS total_retweets,

    SUM(comment_replies) AS total_replies,

    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement,

    ROUND(
        AVG(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        2
    ) AS average_engagement,

    ROUND(
        AVG(sentiment_score),
        4
    ) AS average_sentiment

FROM posts

WHERE datetime IS NOT NULL

GROUP BY DATE_FORMAT(datetime, '%Y-%m')

ORDER BY analysis_month;


-- ============================================================
-- 16. SENTIMENT SUMMARY BY CATEGORY
-- ============================================================

CREATE OR REPLACE VIEW sentiment_category_summary AS
SELECT
    sentiment_category,

    COUNT(*) AS total_posts,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(
            (SELECT COUNT(*) FROM posts),
            0
        ),
        2
    ) AS percentage_of_posts,

    ROUND(
        AVG(sentiment_score),
        4
    ) AS average_sentiment_score,

    SUM(comment_likes) AS total_likes,

    SUM(comment_retweets) AS total_retweets,

    SUM(comment_replies) AS total_replies,

    SUM(
        comment_likes
        + comment_retweets
        + comment_replies
    ) AS total_engagement

FROM posts

GROUP BY sentiment_category

ORDER BY total_posts DESC;


-- ============================================================
-- 17. DASHBOARD KPI SUMMARY
-- ============================================================

CREATE OR REPLACE VIEW dashboard_kpi_summary AS
SELECT

    COUNT(*) AS total_posts,

    COALESCE(
        SUM(comment_likes),
        0
    ) AS total_likes,

    COALESCE(
        SUM(comment_retweets),
        0
    ) AS total_retweets,

    COALESCE(
        SUM(comment_replies),
        0
    ) AS total_replies,

    COALESCE(
        SUM(
            comment_likes
            + comment_retweets
            + comment_replies
        ),
        0
    ) AS total_engagement,

    COALESCE(
        ROUND(
            AVG(
                comment_likes
                + comment_retweets
                + comment_replies
            ),
            2
        ),
        0
    ) AS average_engagement_per_post,

    COALESCE(
        ROUND(
            AVG(sentiment_score),
            4
        ),
        0
    ) AS average_sentiment_score,

    SUM(
        CASE
            WHEN sentiment_category = 'Positive'
            THEN 1
            ELSE 0
        END
    ) AS positive_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Neutral'
            THEN 1
            ELSE 0
        END
    ) AS neutral_posts,

    SUM(
        CASE
            WHEN sentiment_category = 'Negative'
            THEN 1
            ELSE 0
        END
    ) AS negative_posts

FROM posts;


-- ============================================================
-- 18. DATA QUALITY CHECK
-- ============================================================

CREATE OR REPLACE VIEW data_quality_summary AS
SELECT

    COUNT(*) AS total_rows,

    SUM(
        CASE
            WHEN id IS NULL OR id = ''
            THEN 1
            ELSE 0
        END
    ) AS missing_ids,

    SUM(
        CASE
            WHEN username IS NULL OR username = ''
            THEN 1
            ELSE 0
        END
    ) AS missing_usernames,

    SUM(
        CASE
            WHEN datetime IS NULL
            THEN 1
            ELSE 0
        END
    ) AS missing_dates,

    SUM(
        CASE
            WHEN comment IS NULL OR comment = ''
            THEN 1
            ELSE 0
        END
    ) AS missing_comments,

    SUM(
        CASE
            WHEN comment_likes < 0
            THEN 1
            ELSE 0
        END
    ) AS invalid_likes,

    SUM(
        CASE
            WHEN comment_retweets < 0
            THEN 1
            ELSE 0
        END
    ) AS invalid_retweets,

    SUM(
        CASE
            WHEN comment_replies < 0
            THEN 1
            ELSE 0
        END
    ) AS invalid_replies

FROM posts;


-- ============================================================
-- 19. VERIFY ALL VIEWS
-- ============================================================

SHOW FULL TABLES
WHERE TABLE_TYPE = 'VIEW';


-- ============================================================
-- 20. TEST MAIN DASHBOARD KPI VIEW
-- ============================================================

SELECT *
FROM dashboard_kpi_summary;


-- ============================================================
-- 21. TEST ENGAGEMENT VIEW
-- ============================================================

SELECT *
FROM post_engagement_analysis
LIMIT 10;


-- ============================================================
-- 22. TEST AUTHOR ANALYTICS
-- ============================================================

SELECT *
FROM top_authors
LIMIT 10;


-- ============================================================
-- 23. TEST SENTIMENT ANALYTICS
-- ============================================================

SELECT *
FROM sentiment_category_summary;


-- ============================================================
-- 24. TEST DATA QUALITY
-- ============================================================

SELECT *
FROM data_quality_summary;