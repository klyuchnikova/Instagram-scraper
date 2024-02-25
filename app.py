from os.path import dirname, realpath, basename
from os import curdir
import logging
from app.config import load_configuration
from app.storage import InstagramStorage
from selenium import webdriver
from app.scraping import scrape_instagram
import sys


def init():
    global ROOT_DIR
    ROOT_DIR = dirname(realpath(__file__))
    if basename(realpath(curdir)) != "Instagram-scraper":
        logging.warning(
            f"The script is not run from project directory, please cd to {ROOT_DIR}"
        )
        exit(0)

    if sys.prefix == sys.base_prefix:
        logging.warning("Your code is not running inside a virtual environment.")
        exit(0)


def main():
    global ROOT_DIR
    init()
    configuration = load_configuration(ROOT_DIR)
    storage = InstagramStorage(folder_path=configuration.SCRAPER_OUTPUT_PATH)
    driver = webdriver.Chrome()
    try:
        scrape_instagram(storage, driver, configuration)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
