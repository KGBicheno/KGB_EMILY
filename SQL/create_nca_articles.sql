CREATE TABLE nca_articles (
    page_url VARCHAR(255) NOT NULL PRIMARY KEY,
    title VARCHAR(255),
    headtext VARCHAR(255),
    byline VARCHAR(255),
    authors VARCHAR(255)[],
    print_date TIMESTAMPTZ,
    tease TEXT,
    bodytext TEXT[],
    keywords VARCHAR,
    tags VARCHAR(255)[]
)