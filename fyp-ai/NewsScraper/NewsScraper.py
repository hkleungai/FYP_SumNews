from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
from multiprocessing.pool import ThreadPool
import os
import newspaper
import re
import requests
from selenium.webdriver import Chrome, ChromeOptions 
from selenium.webdriver.chrome.webdriver import WebDriver
import shutil
import threading
import time
from typing import Callable, List, Union, Optional
import validators

from Article import Article

class NewsScraper(object):
    def get_article_urls_from_api_url(self, API_URL: str) -> List[str]:
        articles_urls = requests.get(f'{API_URL}/articles?should_get_url_only=true').json()
        valid_article_urls = [url for url in articles_urls if self.__is_valid_url(url)]
        return valid_article_urls

    def get_article_urls_from_db_location(self, db_location: str) -> List[str]:
        article_urls_from_db_location = []

        news_folder_path = os.path.join(db_location, 'news')
        article_folder_names = os.listdir(news_folder_path)
        for article_folder_name in article_folder_names:
            article_folder_path = os.path.join(news_folder_path, article_folder_name)
            article_file_names = os.listdir(article_folder_path)
            for article_file_name in article_file_names:
                article_file_path = os.path.join(article_folder_path, article_file_name)
                with open(article_file_path, "r", encoding="utf-8") as file:
                    article_urls_from_db_location.append(json.load(file)['url'] or None)

        article_urls_from_db_location = list(set(filter(
            self.__is_valid_url, 
            article_urls_from_db_location
        )))

        return article_urls_from_db_location

    def scrape_article_urls(self, existing_article_urls) -> List[str]:
        article_urls: List[str] = []
        scrapers: List[Callable[[List[str]], None]] = [
            self.__scrape_scmp,
            self.__scrape_rthk,
            self.__scrape_hkfp, # success with request
            self.__scrape_standard, # success with request
            self.__scrape_bbc, # success with newspaper
            self.__scrape_reuters, # success with newspaper
            self.__scrape_fox, # success with newspaper
            # self.__scrape_cnn, # success with newspaper
            # self.__scrape_dailymail, # success with newspaper
            self.__scrape_guardian, # success with newspaper
            self.__scrape_usatoday, # success with newspaper
            # self.__scrape_nytimes, # success with newspaper
            self.__scrape_nbc, # success with newspaper
        ]

        # Sequential version
        # browser = self.__get_browser()
        # for scraper in scrapers:
        #     scraper(article_urls)
        # browser.quit()

        # Parallel version
        ThreadPool(10).map(self.__scraper_map(article_urls), scrapers)

        new_article_urls = list(filter(
            lambda news_url: news_url not in existing_article_urls, 
            article_urls
        ))

        return new_article_urls

    def download_articles_by_urls(self, article_urls: List[str]) -> List[Article]:
        articles = []
        
        # Sequential version
        # for article_url in article_urls:
        #     self.__download_article(url, articles)

        # Parallel version
        ThreadPool(40).map(self.__download_map(articles), article_urls)

        return articles

    def __init__(self) -> None:
        self.__THREADING_LOCAL = threading.local()

        # Regexp compilation done on __init__() so that
        # they would not be recomputed upon each round of scraping.
        self.__SCMP_URL_REGEXP = re.compile(r'^(?!.*\#comments)(https://www.scmp.com/(?!(.*(lifestyle|comment|opinion|magazines).*))(.+)/article/.+)$')
        self.__RTHK_URL_REGEXP = re.compile(r'^https://news.rthk.hk/rthk/en/component/k2/[0-9]{7}-[0-9]{8}.htm$')
        self.__HKFP_URL_REGEXP = re.compile(r'^https://hongkongfp.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/.+$')
        self.__STANDARD_URL_REGEXP = re.compile(r'^https://www.thestandard.com.hk/(breaking|section)-news/section/.+$')
        self.__BBC_URL_REGEXP = re.compile(r'^https://www.bbc.com/news/world\-.+\-[0-9]{8}$')
        self.__REUTERS_URL_REGEXP = re.compile(r'^https://www.reuters.com/article/.+$')
        self.__FOX_URL_REGEXP = re.compile(r'^https://www.foxnews.com/(world|politics|tech|science|sports)/.+$')
        self.__CNN_URL_REGEXP = re.compile(r'^https://edition.cnn.com/[0-9]{4}/[0-9]{2}/.+/index.html$')
        self.__DAILYMAIL_URL_REGEXP = re.compile(r'^(?!.*\#(video|comments))https://www.dailymail.co.uk/news/article-[0-9]{7}/.+$')
        self.__GUARDIAN_URL_REGEXP = re.compile(r'^(?!.*-video)https://www.theguardian.com/(?!.*(live|gallery|commentisfree|help|video|lifeandstyle))(.+)/[0-9]{4}/[a-z]{3}/[0-9]{2}/(?!.*picture.*).+$')
        self.__USATODAY_URL_REGEXP = re.compile(r'^https://www.usatoday.com/story/news/.+/[0-9]{4}/[0-9]{2}/[0-9]{2}/.+$')
        self.__NYTIMES_URL_REGEXP = re.compile(r'^https://www.nytimes.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/world/.+\.html$')
        self.__NBC_URL_REGEXP = re.compile(r'^https://www.nbcnews.com/(?!(.*(slideshow|video|live-blog|nbcblk|shopping|opinion|veteran-services).*)).+/.+(-n[0-9]+)$')

    # The enter-exit pair 
    # - favors the use of with-as syntax, and
    # - helps perform file cleaning once the with-as block is ended or when there is keyboard-interrupt
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # Such local file-write indirectly disable multi-user file sharing on a remote server.
        # Plus enabling it seems does not make the code run faster in current use case. 
        tmp_path = '/tmp/.newspaper_scraper'
        os.path.exists(tmp_path) and os.path.isdir(tmp_path) and shutil.rmtree(tmp_path)
        return True

    '''
    - A try-catch block is set so that no single network failure would break the whole scraping.
      And a retrial on the same url is not immediately performed,
      with the hope that such article should be able to obtained 5 mins later.

    - For maximizing the scraping efficiency, 
      each news domain is tested with `newspaper` (fastest) first, then `bs4`, and finally `selenium` (slowest).
      And to balance for the speed and result completeness, in some cases we adopt a slower scraping approach, 

    - For scrapers that are going to employ this function,
      they would specify `is_capable_with_newspaper_build` or `is_destination_page_static` in the function call.
      Even for those adopting the default selenium approach
      (in which the two flags can just follow the default falsy values),
      they would still own a dummy flag assignment `is_destination_page_static = False` for consistency. 
    '''
    def __scrape_from_one_source(
        self,
        destination_url: str,
        regexp: re.Pattern,
        is_capable_with_newspaper_build: bool = False,
        is_destination_page_static: bool = False,
        article_urls: List[str] = [],
    ) -> None:
        try:
            if is_capable_with_newspaper_build:
                # Explicitly setting memoize_articles to false
                # can help prevent caching between newspaper.build() calls,
                # in which such caching if unfortunately exists could trigger empty returns.
                # For details check https://github.com/codelucas/newspaper/issues/243#issuecomment-218248310  
                paper = newspaper.build(destination_url, memoize_articles = False)
                search_urls = self.__article_url_selectors(
                    input_with_urls = paper.articles,
                    custom_lambda = lambda article: article.url,
                    custom_regexp = regexp
                )
                article_urls.extend(search_urls)
            elif is_destination_page_static:
                html = requests.get(destination_url)
                html.raise_for_status() # Check if things are rendered well
                soup = BeautifulSoup(html.text, 'html.parser')
                search_urls = self.__article_url_selectors(
                    input_with_urls = soup.find_all('a', href=True),
                    custom_lambda = lambda a_tag: a_tag['href'],
                    custom_regexp = regexp
                )
                article_urls.extend(search_urls)
            else: 
                browser = self.__get_browser()
                browser.get(destination_url) 
                time.sleep(3) # Exec time.sleep for dynamic loading and avoiding threads conflicts
                search_urls = self.__article_url_selectors(
                    input_with_urls = browser.find_elements_by_tag_name('a'),
                    custom_lambda = lambda a_tag: a_tag.get_attribute('href'),
                    custom_regexp = regexp
                )
                article_urls.extend(search_urls)
                self.__close_browser(browser)
        except Exception as e:
            self.__close_browser()
            print(e)

    def __scrape_scmp(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.scmp.com/hk',
            regexp = self.__SCMP_URL_REGEXP,
            is_destination_page_static = False,
            # is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_rthk(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://news.rthk.hk/rthk/en/',
            regexp = self.__RTHK_URL_REGEXP,
            is_destination_page_static = False,
            article_urls = article_urls,
        )

    def __scrape_hkfp(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://hongkongfp.com/',
            regexp = self.__HKFP_URL_REGEXP,
            is_destination_page_static = True,
            article_urls = article_urls,
        )

    def __scrape_standard(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.thestandard.com.hk/',
            regexp = self.__STANDARD_URL_REGEXP,
            is_destination_page_static = True,
            article_urls = article_urls,
        )

    def __scrape_bbc(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.bbc.com/news/world',
            regexp = self.__BBC_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_reuters(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.reuters.com/world',
            regexp = self.__REUTERS_URL_REGEXP,
            # is_destination_page_static = False,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_fox(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'http://foxnews.com/world',
            regexp = self.__FOX_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            # is_destination_page_static = True,
            article_urls = article_urls,
        )

    # The scraping returns too many results,
    # and hence it is now not in the __scraper_map()
    def __scrape_cnn(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://edition.cnn.com/',
            regexp = self.__CNN_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            # is_destination_page_static = True,
            article_urls = article_urls,
        )

    # The scraping returns too many results,
    # and hence it is now not in the __scraper_map()
    def __scrape_dailymail(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.dailymail.co.uk/news/worldnews/index.html',
            regexp = self.__DAILYMAIL_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            # is_destination_page_static = False,
            article_urls = article_urls,
        )

    def __scrape_guardian(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.theguardian.com/world',
            regexp = self.__GUARDIAN_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_usatoday(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.usatoday.com/news/world/',
            regexp = self.__USATODAY_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_nytimes(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.nytimes.com/section/world',
            regexp = self.__NYTIMES_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )

    def __scrape_nbc(self, article_urls: List[str] = []) -> None:
        self.__scrape_from_one_source(
            destination_url = 'https://www.nbcnews.com/world',
            regexp = self.__NBC_URL_REGEXP,
            is_capable_with_newspaper_build = True,
            article_urls = article_urls,
        )
    
    def __get_browser(self) -> WebDriver:
        browser = getattr(self.__THREADING_LOCAL, 'browser', None)
        while browser == None:
            try: 
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                # $ apt install chromium-chromedriver
                browser = Chrome('chromedriver', options=chrome_options)
                setattr(self.__THREADING_LOCAL, 'browser', browser)
                break
            except Exception as e:
                print(e)
                continue
        return browser

    def __close_browser(self, browser: WebDriver = None):
        browser = browser or getattr(self.__THREADING_LOCAL, 'browser', None)
        if browser != None:
            browser.quit()
            setattr(self.__THREADING_LOCAL, 'browser', None)

    # Map article_urls to one specific scraper
    # so that that scraper can in turn put url results into article_urls
    def __scraper_map(self, article_urls: List[str] = []):
        def function_to_be_returned(scraper: Callable[[List[str]], None]):
            scraper(article_urls)
        return function_to_be_returned
    
    def __article_url_selectors(
        self,
        input_with_urls,
        custom_lambda,
        custom_regexp: re.Pattern,
    ): 
        return list(filter(
            lambda url: type(url) == str and custom_regexp.match(url),
            list(set(map(custom_lambda, input_with_urls)))
        )) 

    '''
    - A try-catch block is set so that no single network failure would break the whole scraping.
      And a retrial on the same url is not immediately performed,
      with the hope that such article should be able to obtained 5 mins later.

    - The approach is, 
      1. Employ pre-built download() from the 3rd-party newspaper module first,
         in which such download() call should already give 
         partial, if not all, desirable information on the news pieces.
      2. Then introduce appropriate fix on incorrect data entries by examining the source html.
         Such procedure expectedly invokes an extensive use of the bs4 module.
    '''
    def __download_article(self, url: str, articles: List[Article]) -> Optional[Article]:
        try:
            article = newspaper.Article(url)
            article.download()
            time.sleep(0.01)
            article.parse()
            
            soup = BeautifulSoup(article.html, 'html.parser')
            date_added, source, text = None, None, None
            images = article.images
            
            # Could need more noise filtering for scmp
            # coz the web-page is so dynamic that no good html elements can be exploited.
            # It means what's inside articleBody can contain certain noise.
            if self.__SCMP_URL_REGEXP.match(url): 
                date_added_text = soup.find('meta', { 'property': 'article:published_time' })['content']
                date_added = str(datetime.strptime(date_added_text, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo = timezone.utc))

                # text = re.findall(r'{"type":"p","children":\[{"type":"text","data":"([^"}\]]*)"', article.html)
                text = re.compile(r'"articleBody":"([^"]*)",').search(article.html).groups()[0]
                # text = re.compile(r'<script>window.__APOLLO_STATE__=(.*)</script><script>').search(article.html).groups()[0]
                # text = json.loads(text)
            
            if self.__RTHK_URL_REGEXP.match(url):
                date_added_text = soup.find('div', { 'class': 'createddate' }).text.replace(' HKT ', ' ')
                date_added = str(datetime.fromisoformat(date_added_text).replace(tzinfo = timezone.utc))
                images = list(filter(
                    lambda image_url: not any(x in image_url for x in ['frontend_images', '.gif']), 
                    images
                ))
                source = 'RTHK News'
                text = soup.find("div", {"class": "itemFullText"}).text.strip()
            
            if self.__HKFP_URL_REGEXP.match(url):
                date_added_text = soup.find('meta', { 'property': 'article:published_time' })['content']
                date_added = str(datetime.strptime(date_added_text, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo = timezone.utc))
                
                main_content = soup.find('div', {'class', 'entry-content'})
                falsy_images = [
                    image['src']
                    for article_tag in main_content.find_all('article', { 'id': None })
                    for image in article_tag.find_all('amp-img')
                ]
                images = [
                    image['src'] for image in main_content.find_all('amp-img')
                    if image['src'] not in falsy_images and 'hkfp' not in image['src'] and 'hkfp' not in image['alt']
                ]

                # Filtering an falsy sponsorship text that may or may not appear in articles.
                optional_falsy_column = soup.find('div', { 'class': 'wp-block-columns' })
                optional_falsy_p_tags = optional_falsy_column.find_all('p') if optional_falsy_column != None else [] 
                falsy_text = [
                    p_tag.text for p_tag in optional_falsy_p_tags
                ] + [
                    p_tag.text for p_tag in soup.find('section', { 'id': 'text-3' }).find_all('p')
                ]
                text = ' '.join(
                    p_tag.text.strip() for p_tag in main_content.find_all('p')
                    if p_tag.text not in falsy_text     
                )

            if self.__STANDARD_URL_REGEXP.match(url):
                date_added_text = re.compile(r'([0-9]{1,2}\s.*)').search(
                    soup.find('span', { 'class': 'pull-left' }).text
                ).groups()[0].strip()
                date_added_format = '%d %b %Y %H:%M %p' if date_added_text[-1] == 'm' else '%d %b %Y'  
                date_added = str(datetime.strptime(date_added_text, date_added_format).replace(tzinfo = timezone.utc))

                main_content = soup.find('div', {'class', 'content'})
                figure = main_content.find('figure')
                images = [figure.find('img')['src']] if figure != None else [] 

                text = ' '.join(p_tag.text.strip() for p_tag in main_content.find_all('p'))

            if self.__BBC_URL_REGEXP.match(url):
                time_tag = soup.find('time')
                if time_tag == None: # time_tag being None means it is a video.
                    return
                date_added_text = time_tag['datetime']
                date_added = str(
                    datetime.strptime(re.sub(r'\.[0-9]{3}', '', date_added_text), '%Y-%m-%dT%H:%M:%S%z'
                ).replace(tzinfo = timezone.utc))

                main_content = soup.find('article')
                images = [
                    image['srcset'].split(', ')[-1][:-5] 
                    for image in main_content.find_all('img', { 'srcset' : True })
                    if '.jpg' in image['srcset'].split(', ')[-1]
                ]

                text = ' '.join(
                    p_tag.text.strip() 
                    for text_div in main_content.find_all('div', { 'data-component': 'text-block' })
                    for p_tag in text_div.find_all('p')
                )

            if self.__REUTERS_URL_REGEXP.match(url):
                images = [image for image in images if 'https://s1.reutersmedia.net' not in image]

                main_content = soup.find('div', { 'class': 'ArticleBodyWrapper' })
                if main_content == None: # main_content being None means it is NOT a valid article.
                    return
                falsy_text = [
                    p_tag.text 
                    for div in main_content.select('div[class*="ArticleBody-byline-container-"]')
                    for p_tag in div
                ] + [
                    p_tag.text
                    for div in main_content.select('div[class*="Attribution-attribution-"]')
                    for p_tag in div
                ] + [
                    p_tag.text
                    for div in main_content.select('div[class*="TrustBadge-trust-badge-"]')
                    for p_tag in div
                ] + [
                    p_tag.text
                    for div in main_content.select('div[class*="About-about-"]')
                    for p_tag in div
                ] 
                text = ' '.join(
                    p_tag.text.strip() for p_tag in main_content.find_all('p')
                    if p_tag.text not in falsy_text
                )

                source = 'Reuters'

            if self.__FOX_URL_REGEXP.match(url):
                date_added_text = soup.find('meta', { 'data-hid': 'dcterms.created' })['content']
                date_added = str(datetime.strptime(date_added_text, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo = timezone.utc))

                main_content = soup.find('div', { 'class': 'article-body' })
                if main_content == None: # main_content being None means it is NOT a valid article.
                    return

                images = [img['src'] for img in main_content.find_all('img')]

                falsy_text = [
                    re.sub(r'\n\s+', '', p_tag.text) 
                    for div in main_content.find_all('div', { 'class': 'caption' })
                    for p_tag in div.find_all('p')
                ] + [
                    re.sub(r'\n\s+', '', strong.text)
                    for strong in main_content.find_all('strong')
                ] 
                text_list = [
                    re.sub(r'\n\s+', '', p_tag.text.strip()) 
                    for p_tag in main_content.find_all('p')
                ]
                text = ' '.join(text for text in text_list if text not in falsy_text)

            if self.__GUARDIAN_URL_REGEXP.match(url):
                date_added_meta_tag = soup.find('meta', { 'property': 'article:published_time' }) 
                date_added_time_tag = soup.find('time', { 'itemprop': 'datePublished' })
                date_added_text = (
                    re.sub(r'\.[0-9]{3}', '', date_added_meta_tag['content'])
                ) if date_added_meta_tag != None else (
                    date_added_time_tag['datetime']
                ) if date_added_time_tag != None else (
                    None
                )
                date_added = (
                    str(datetime.strptime(date_added_text, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo = timezone.utc))
                ) if date_added_text != None else (
                    None
                )

                images = [image for image in images if '.jpg' in image]

                main_content = (
                    soup.select('div[class*="article-body"]') or soup.select('div[class*="content__main-column"]')
                )[0]
                text = ' '.join(
                    p_tag.text.strip() for p_tag in main_content.find_all('p')
                )

            if self.__USATODAY_URL_REGEXP.match(url):
                text = ' '.join(
                    p_tag.text.strip() for p_tag in soup.find_all('p', { 'class': 'gnt_ar_b_p' })
                    if not re.compile(r'^Contributing:\s.+$').match(p_tag.text) 
                )

            if self.__NBC_URL_REGEXP.match(url):
                images = [image for image in images if '100x100' not in image]

                main_content = soup.find('div', { 'class': 'article-body__content' })
                falsy_text = [
                    em.text.strip() + '.'
                    for em in main_content.find_all('em')
                ]
                text = ' '.join(
                    p_tag.text.strip() for p_tag in main_content.find_all('p')
                    if p_tag.text not in falsy_text
                )

            article = Article(
                article = article,
                date_added = date_added,
                photos_url = list(set(filter(self.__is_valid_url, images))),
                source = source,
                text = text,
            )

            articles.append(article)
        except Exception as e:
            print(e)
            print(url)

    def __download_map(self, articles: List[Article]):
        def function_to_be_returned(url: str) -> None:
            self.__download_article(url, articles)
        return function_to_be_returned

    def __is_valid_url(self, url):
        return type(url) == str and validators.url(url) 
