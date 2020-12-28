SELECT articles.page_url, articles.print_date, counts.body_counts, counts.headline_counts, counts.tease_counts 
FROM articles 
INNER JOIN counts ON articles.page_url=counts.page_url;