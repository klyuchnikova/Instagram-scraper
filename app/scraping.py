import json
from .config import Configuration
from .storage import InstagramStorage
from .instagram_api import InstagramApi, Post
import typing as tp
from selenium import webdriver
import logging


def _load_companies(
    companies_file: str, list_of_companies: tp.List[str]
) -> tp.Dict[str, tp.List[str]]:
    with open(companies_file, "r") as file:
        all_comapnies = json.load(file)
    if len(list_of_companies) == 0:
        return all_comapnies
    relevant_companies = dict(
        (k, all_comapnies[k]) for k in list_of_companies if k in all_comapnies
    )
    return relevant_companies


def scrape_instagram(
    storage: InstagramStorage,
    web_driver: webdriver.Chrome,
    configuration: Configuration,
):
    logging.info(
        "Startig app with "
        + ("scraping images" if configuration.SCRAPE_IMAGES else "no image scraping")
        + ", "
        + (
            "scraping comments"
            if configuration.SCRAPE_COMMENTS
            else "no comment scraping"
        )
    )

    companies = _load_companies(
        companies_file=configuration.COMPANIES_FILE_PATH,
        list_of_companies=configuration.COMPANIES,
    )
    instagram = InstagramApi(
        web_driver=web_driver,
        scape_comments=configuration.SCRAPE_COMMENTS,
        scrape_tags=True,
    )
    if configuration.SCRAPE_COMMENTS:
        instagram.login()

    if configuration.SCRAPE_POSTS:
        scraped_posts = scrape_posts_by_tags(storage, instagram, companies)
    else:
        scraped_posts = storage.get_all_with_no_image()

    if configuration.SCRAPE_IMAGES:
        scrape_images_for_posts(scraped_posts, storage, instagram)
    if configuration.SCRAPE_COMMENTS:
        scrape_comments_for_posts(scraped_posts, storage, instagram)


def scrape_posts_by_tags(
    storage: InstagramStorage, instagram, companies: tp.Dict[str, tp.List[str]]
) -> tp.List[Post]:
    def filter_post(post: Post) -> bool:
        # returns true if post passes the filter
        return not storage.is_post_present(post.id)

    posts = []  # tp.List[Post]
    for company, tags in companies.items():
        for post in instagram.scrape_posts_by_tags(tags, filter_post):
            post.company = company
            storage.update_post_info(post)
            posts.append(post)
    storage.save_table_changes()  # don't forget this step :)
    return posts


def scrape_images_for_posts(
    posts: tp.List[Post], storage: InstagramStorage, instagram: InstagramApi
):
    try:
        for post in posts:
            image = instagram.scrape_image_by_url(post.image_url)
            storage.save_image_for_post(post.id, image)
    finally:
        storage.save_table_changes()  # don't forget this step :)


def scrape_comments_for_posts(
    posts: tp.List[Post], storage: InstagramStorage, instagram: InstagramApi
):
    try:
        for post in posts:
            comments = instagram.scrape_comments(post.id, max_comments=100)
            storage.save_image_for_post(post.id, comments)
    finally:
        storage.save_table_changes()  # don't forget this step :)
