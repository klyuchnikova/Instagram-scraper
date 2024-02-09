import json
from config import Configuration
from storage import InstagramStorage
from instagram_api import InstagramApi, Post
import typing as tp


def _load_companies(companies_file, list_of_companies) -> tp.Dict[str, tp.List[str]]:
    with open(companies_file, "r") as file:
        all_comapnies = json.load(file)
    relevant_companies = dict(
        (k, all_comapnies[k]) for k in list_of_companies if k in all_comapnies
    )
    return relevant_companies


def scrape_instagram(
    storage: InstagramStorage, web_driver, configuration: Configuration
):
    companies = _load_companies(configuration.COMPANIES_FILE_PATH)
    instagram = InstagramApi(
        web_driver=web_driver,
        scape_comments=configuration.SCRAPE_COMMENTS,
        scrape_tags=True,
    )
    if configuration.SCRAPE_COMMENTS:
        instagram.login()

    def filter_post(post: Post) -> bool:
        # returns true if post passes the filter
        return not storage.is_post_present(post.id)

    for company, tags in companies.items():
        for post in instagram.scrape_posts_by_tags(tags, filter_post):
            post.company = company
            storage.update_post_info(post)
    scrape_images_for_posts()


def scrape_images_for_posts(
    posts: tp.List[Post], storage: InstagramStorage, instagram: InstagramApi
):
    for post in posts:
        image = instagram.scrape_image_by_url(post.image_url)
        storage.save_image_for_post(post.id, image)
