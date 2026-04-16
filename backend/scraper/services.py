from urllib.parse import urljoin

from django.db import transaction
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from books.models import Book
from rag.indexer import BookEmbeddingIndexer
from rag.insights import BookInsightService


class SeleniumBookScraper:
    """Scrape books from books.toscrape.com and store them in the database."""

    SOURCE_URL = "https://books.toscrape.com/"
    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def __init__(self, headless=True):
        self.headless = headless

    def _build_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1400,900")
        return webdriver.Chrome(options=options)

    def scrape_books(self, limit=20):
        saved_books = []

        with self._build_driver() as driver:
            driver.get(self.SOURCE_URL)
            book_cards = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

            for card in book_cards[:limit]:
                title_element = card.find_element(By.CSS_SELECTOR, "h3 a")
                title = title_element.get_attribute("title") or title_element.text.strip()
                detail_url = urljoin(self.SOURCE_URL, title_element.get_attribute("href"))
                rating_text = card.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class").split()[-1]
                rating = self.RATING_MAP.get(rating_text)

                driver.get(detail_url)
                description = self._extract_description(driver)

                book, _ = Book.objects.update_or_create(
                    url=detail_url,
                    defaults={
                        "title": title,
                        "author": "Unknown Author",
                        "description": description,
                        "rating": rating,
                    },
                )
                BookInsightService().generate_insights(book, persist=True)

                try:
                    BookEmbeddingIndexer().index_book(book)
                except Exception:
                    pass

                saved_books.append(book)

                driver.back()

        return saved_books

    def _extract_description(self, driver):
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, "#product_description ~ p")
            return description_element.text.strip()
        except Exception:
            return ""
