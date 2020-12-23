CREATE TABLE counts (
    page_url VARCHAR NOT NULL PRIMARY KEY,
    headline_counts INT,
    tease_counts INT,
    body_counts INT
)