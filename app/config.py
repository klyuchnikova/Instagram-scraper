import os
import logging
from dotenv import load_dotenv
import argparse


class Configuration:
    # absolute path to the directory all filed will be stored
    SCRAPER_OUTPUT_PATH = None

    # instagram authentification
    INSTAGRAM_LOGIN = None
    INSTAGRAM_PASSWORD = None

    # optionally we could only scrape parts of what we need
    SCRAPE_POSTS = True
    SCRAPE_IMAGES = False
    SCRAPE_COMMENTS = False

    # list of comapny names that are being scraped
    COMPANIES = []
    COMPANIES_FILE_PATH = None

    def __init__(self, args: argparse.Namespace, root_dir: str):
        self.ENV_PATH = os.path.join(root_dir, ".env")
        self.COMPANIES_FILE_PATH = os.path.join(root_dir, "companies.json")
        self._load_from_env()
        self._load_from_argparse(args)
        self._validate()

    def _load_from_argparse(self, args: argparse.Namespace):
        self.SCRAPER_OUTPUT_PATH = args.output_path or self.SCRAPER_OUTPUT_PATH

        self.INSTAGRAM_LOGIN = args.instagram_login or self.INSTAGRAM_LOGIN
        self.INSTAGRAM_PASSWORD = args.instagram_password or self.INSTAGRAM_PASSWORD

        self.SCRAPE_POSTS = False if not args.scrape_posts else True
        self.SCRAPE_IMAGES = args.scrape_images or self.SCRAPE_IMAGES
        self.SCRAPE_COMMENTS = args.scrape_comments or self.SCRAPE_COMMENTS

        self.COMPANIES = args.companies or self.COMPANIES

    def _load_from_env(self):
        if not self.ENV_PATH or not os.path.exists(self.ENV_PATH):
            logging.info("couln't find configuration file, skipping it")
            return
        logging.info("loading configuration file")
        load_dotenv(self.ENV_PATH)
        self.SCRAPER_OUTPUT_PATH = (
            os.getenv("SCRAPER_OUTPUT_PATH") or self.SCRAPER_OUTPUT_PATH
        )
        self.INSTAGRAM_LOGIN = os.getenv("INSTAGRAM_LOGIN")
        self.INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
        self.SCRAPE_IMAGES = os.getenv("SCRAPE_IMAGES")
        self.SCRAPE_COMMENTS = os.getenv("SCRAPE_COMMENTS")

    def _validate(self):
        if self.SCRAPE_COMMENTS and (
            self.INSTAGRAM_LOGIN is None or self.INSTAGRAM_PASSWORD is None
        ):
            raise AttributeError(
                "For scraping instagram comments authentication is needed, please provide login and password"
            )


def load_configuration(root_dir: str) -> Configuration:
    parser = argparse.ArgumentParser(description="args for Instagram scraper")
    parser.add_argument(
        "-il",
        "--instagram-login",
        metavar="login",
        type=str,
        help="Instagram login for authorization",
        required=False,
    )
    parser.add_argument(
        "-ip",
        "--instagram-password",
        metavar="password",
        type=str,
        help="Instagram password for authorization",
        required=False,
    )
    parser.add_argument(
        "-op",
        "--output-path",
        metavar="output",
        type=str,
        required=False,
        help="Absolute path to output folder where scraped results will be saved.\n",
    )
    parser.add_argument(
        "--scrape-posts",
        action="store_true",
        required=False,
        help="Turn on-off scraping posts. If on, firstly the general posts by tags will be scraped and stored in content.csv. Else, the future scraping will be applied to all empty fields found in the table.\n",
    )
    parser.add_argument(
        "--scrape-images",
        action="store_true",
        required=False,
        help="Turn on-off scraping images. If on, they will be saved along with posts in the folder, but only AFTER the table of posts was formed.\n",
    )
    parser.add_argument(
        "--scrape-comments",
        action="store_true",
        required=False,
        help="Turn on-off scraping comments. If on, the authorization is needed.\n",
    )
    parser.add_argument(
        "--companies",
        nargs="+",
        required=False,
        help="List companies you wish to scrape from. They are expected to be keys in companies.json that lies in the root. If none provided, will use ALL comapnies found in the file.\n",
    )
    args = parser.parse_args()
    return Configuration(args, root_dir)
