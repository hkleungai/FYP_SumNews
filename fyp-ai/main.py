def main():
    from datetime import datetime
    import logging
    import random
    import requests
    import tensorflow as tf
    import time

    from Article import Article
    from NewsGroup import NewsGroup
    from NewsScraper import NewsScraper
    from similarity import add_articles_to_current_clusters, cluster_ungrouped_articles

    tf.get_logger().setLevel(logging.ERROR)

    API_URL = "http://localhost:3000"

    INTERVAL = 45 * 60 # 45 mins, converted to seconds

    while True:
        start_time = time.time()
        print(f'A new iteration starts. Current time is {datetime.now().strftime("%H:%M:%S")}')
        print()

        # TODO: Consider performing article grouping more frequently, 
        # rather than having it in sync with the web scraping in each iteration.
        # - Web scraping from 10 sources can flood the api-endpoint with 400-500 articles in each round.
        # - Article grouping with sample_size = 100 can already take 60 to 80 minutes

        # Web scraping
        with NewsScraper() as news_scraper_instance:
            existing_article_urls = news_scraper_instance.get_article_urls_from_api_url(API_URL = API_URL)
            scraped_article_urls = news_scraper_instance.scrape_article_urls(existing_article_urls = existing_article_urls)
            scraped_articles = news_scraper_instance.download_articles_by_urls(article_urls = scraped_article_urls)
            scraped_article_dicts = [article.__dict__ for article in scraped_articles]
            request.post(f'{API_URL}/articles', json = scraped_article_dicts)

        # Grouping articles
        current_ungrouped_article_id_list = requests.get(f"{API_URL}/articles/?is_grouped=false&should_get_id_only=true").json()
        random.shuffle(current_ungrouped_article_id_list)
        
        # Without scraping step, and with GPU support
        # num = 30 takes about 15-20 minutes (GPU) / 20-30 minutes (CPU)
        # num = 100 takes about 90-110 minutes (GPU) / 130-140 minutes (CPU)
        # This sampling step can be skipped, 
        # by having `num_of_articles_to_be_processed = len(current_ungrouped_articles)`
        num_of_articles_to_be_processed = 100
        selected_ungrouped_article_id_list = current_ungrouped_article_id_list[:num_of_articles_to_be_processed]

        print('Adding articles to current clusters')
        updated_news_group_ids = add_articles_to_current_clusters(API_URL, selected_ungrouped_article_id_list)
        print('Successfully added articles to current clusters')
        print()

        print('Clustering ungrouped articles')
        new_news_group_ids = cluster_ungrouped_articles(API_URL, selected_ungrouped_article_id_list)
        print('Successfully clustered ungrouped articles')
        print()

        # Summarization and related articles
        print('Adding ungrouped articles into news groups')
        for ng_id in updated_news_group_ids + new_news_group_ids:
            ng_article_ids = requests.get(f"{API_URL}/news/{ng_id}?should_get_articles_and_id_only=true").json()
            articles = [
                Article(article = requests.get(f"{API_URL}/articles/{article_id}?should_get_features_for_summarization").json())
                for article_id in ng_article_ids
            ]
            try: 
                ng = NewsGroup(articles, ng_id)
                ng.process(API_URL) # Sometimes a dimension unmatched error occurs from tf's computation
                del ng.articles
                requests.put(f"{API_URL}/news/{ng_id}", json=ng.__dict__)
            except Exception as e:
                # Such skipping should be safe,
                # since the articles remains ungrouped at the api-endpoint
                # and can be later regrouped by the program.
                print(e)
                print(f'ng.process() fails. Skipping group {ng_id}')
        print('Successfully added ungrouped articles into news groups')
        print()

        end_time = time.time()
        run_time = end_time - start_time 
        run_time_in_min, run_time_in_sec = int(run_time) // 60, round(run_time % 60)
        print(f"---- This iteration takes {run_time_in_min} minutes and {run_time_in_sec} seconds to terminate ----")
        print()

        # Wait until the next cycle
        time.sleep(max(0, INTERVAL - (end_time - start_time)))

if __name__ == "__main__":
    main()
