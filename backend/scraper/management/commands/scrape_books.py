from django.core.management.base import BaseCommand, CommandError

from scraper.services import SeleniumBookScraper


class Command(BaseCommand):
    help = "Scrape book data from books.toscrape.com and save it to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of books to scrape.",
        )
        parser.add_argument(
            "--no-headless",
            action="store_true",
            help="Run the browser with a visible window.",
        )

    def handle(self, *args, **options):
        try:
            scraper = SeleniumBookScraper(headless=not options["no_headless"])
            books = scraper.scrape_books(limit=options["limit"])
        except Exception as exc:
            raise CommandError(f"Scraping failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Scraped and stored {len(books)} books."))
