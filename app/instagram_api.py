import typing as tp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image
import re
import time
import logging
import requests
from io import BytesIO

INSTAGRAM_POST_REGEX = "https://www.instagram.com/p/([a-zA-Z0-9_\-]+)/"
INSTAGRAM_POST_URL_TEMPLATE = "https://www.instagram.com/p/{post_id}/"
INSTAGRAM_TAG_EXPLORE_TEMPLATE = "https://www.instagram.com/explore/tags/{tag_name}/"


class Post:
    def __init__(self, id, image_url, caption, tags=[], comments=[]):
        self.id = id
        self.image_url = image_url
        self.caption = caption
        self.tags = tags
        self.comments = comments
        self.company = None

    @property
    def url(self):
        return INSTAGRAM_POST_URL_TEMPLATE.format(post_id=self.id)

    def add_comment(self, text: str):
        self.comments.append(text)


class InstagramApi:
    def __init__(
        self,
        web_driver: tp.Optional[webdriver.Chrome],
        scape_comments: bool = False,
        scrape_tags: bool = False,
    ):
        self.web_driver = web_driver
        self._scape_comments = scape_comments
        self._scrape_tags = scrape_tags

    def login(self, username: str, password: str):
        self.driver.get("https://www.instagram.com")

        # Wait for the pop-up to appear and close it
        pop_up_path = (
            "/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]"
        )

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, pop_up_path))
            )
            cookie_button = self.driver.find_element(By.XPATH, pop_up_path)
            cookie_button.click()
            time.sleep(2)
        except Exception:
            print("Cookie pop-up not found or already handled.")
            raise

        # Login procedure
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        try:
            WebDriverWait(self.driver, 10).until(EC.url_contains("instagram.com/"))
            print("Login successful!")
        except Exception:
            print("Login failed or timed out.")
            raise

    def scrape_posts_by_tags(
        self,
        tags: tp.List[str],
        filter_function,
        maximum_posts: int = 50,
    ) -> tp.List[Post]:
        posts = []
        for tag in tags:
            if len(posts) >= maximum_posts:
                break
            posts.extend(
                self.scrape_posts_by_tag(
                    tag,
                    maximum_posts=maximum_posts - len(posts),
                    filter_function=filter_function,
                )
            )
        return posts

    def scrape_posts_by_tag(
        self, tag: str, filter_function, maximum_posts: int = 50
    ) -> tp.List[Post]:
        self.driver.get(INSTAGRAM_TAG_EXPLORE_TEMPLATE.format(tag))
        # Wait for the pictures to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._aagv > img"))
        )

        scraped_posts = []
        images = self.driver.find_elements(By.CSS_SELECTOR, "div._aagv > img")
        for image in images:
            image_url = image.get_attribute("src")
            caption = image.get_attribute("alt")
            a_post_elements = list(image.find_elements(By.XPATH, "../../.."))
            if len(a_post_elements) is None:
                raise RuntimeError(
                    f"Couldn't parse post, irregular picture: {image_url}"
                )
            post_url = a_post_elements[0].get_attribute("href")
            match = re.search(INSTAGRAM_POST_REGEX, post_url)
            if not match:
                raise RuntimeError(
                    f"Couldn't parse post, irregular post link: {post_url}"
                )
            post_id = match.group(1)
            found_post = Post(id=post_id, image_url=image_url, caption=caption)
            # later use scrape_post_by_url --!
            if filter_function(found_post):
                scraped_posts.append(found_post)
            if len(scraped_posts) == maximum_posts:
                break
        return scraped_posts

    def scrape_image_by_url(
        self, image_url: str, max_attempts=3
    ) -> tp.Optional[Image.Image]:
        logging.info(f"Downloading img: {image_url}")
        attempts = 0
        while attempts < max_attempts:
            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content))
                else:
                    logging.info(
                        f"Failed to download image, attempt {attempts + 1}/{max_attempts}:"
                        f"bad request {response.status_code}"
                    )
            except Exception as e:
                logging.info(
                    f"Failed to download image, attempt {attempts + 1}/{max_attempts}:"
                    f"{e}"
                )
            attempts += 1
            time.sleep(5)
        return None

    def scrape_post_by_url(
        self,
        post_url: str,
        max_comments: int = 200,
        max_tags: int = 10,
    ) -> Post:
        # --!
        pass
