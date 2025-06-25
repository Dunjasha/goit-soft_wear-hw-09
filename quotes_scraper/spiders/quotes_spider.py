import scrapy
from quotes_scraper.items import QuoteItem, AuthorItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://quotes.toscrape.com/"]

    authors_seen = set()

    def parse(self, response):
        for quote in response.css("div.quote"):
            text = quote.css("span.text::text").get()
            author = quote.css("small.author::text").get()
            tags = quote.css("div.tags a.tag::text").getall()

            yield QuoteItem(text=text, author=author, tags=tags)

            author_url = quote.css("small.author ~ a::attr(href)").get()
            full_author_url = response.urljoin(author_url)

            if full_author_url not in self.authors_seen:
                self.authors_seen.add(full_author_url)
                yield scrapy.Request(full_author_url, callback=self.parse_author)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_author(self, response):
        fullname = response.css("h3.author-title::text").get().strip()
        born_date = response.css("span.author-born-date::text").get()
        born_location = response.css("span.author-born-location::text").get()
        description = response.css("div.author-description::text").get().strip()

        yield AuthorItem(
            fullname=fullname,
            born_date=born_date,
            born_location=born_location,
            description=description
        )
