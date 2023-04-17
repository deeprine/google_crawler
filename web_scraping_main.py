import os
from google_scraper import ImageScraper

if __name__ == "__main__":
    webdriver_path = 'chromedrivers/chromedriver'
    image = os.path.normpath(os.path.join(os.getcwd(), 'photos'))

    keys = ['전기 명판']

    image_counts = 1000
    headless = False
    min_re = (0, 0)
    max_re = (9999, 9999)

    for search_key in keys:
        print(search_key)
        image_scrapper = ImageScraper(webdriver_path, image, search_key, image_counts, headless, min_re, max_re)
        image_urls = image_scrapper.find_image_urls()
        image_scrapper.save_images(image_urls)

    del image_scrapper