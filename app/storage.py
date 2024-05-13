import pandas as pd
import os
import re
from PIL import Image  # type: ignore
from .instagram_api import Post  # type: ignore
import typing as tp
import logging

# WARNING! Does not support concurrency calls
# Preferrable use:
# 1. load posts with comments and save them to storage
# 2. save table
# 3. begin loading images one by one and saving each one


class InstagramStorage:
    CONTENT_TABLE_NAME = "content.csv"
    IMAGE_NAME_REGEX = re.compile(r"img_(\d+)\.jpg")
    IMAGE_NAME_FORMAT = "img_{image_id}.jpg"
    TABLE_COLUMNS = {  # column : pandas dtype
        "post_id": "str",  # necessary (index)
        "tags": "str",
        "company": "str",  # necessary
        "image_url": "str",  # necessary
        "image_file": "str",
        "caption": "str",  # necessary
        "comments": "str",
        "number_comments": "int",
    }

    def __init__(self, folder_path: str = "../data", clear_old=False):
        self.folder_path = os.path.abspath(folder_path)
        if clear_old:
            self._clear_folder_contents()
        os.makedirs(self.folder_path, exist_ok=True)

        self._table_path = os.path.join(self.folder_path, self.CONTENT_TABLE_NAME)
        if os.path.exists(self._table_path):
            self.contents_table = pd.read_csv(self._table_path, index_col="post_id")
        else:
            self.contents_table = pd.DataFrame(
                {
                    column: pd.Series(dtype=column_type)
                    for column, column_type in self.TABLE_COLUMNS.items()
                }
            )
            self.contents_table.set_index("post_id", inplace=True)

        self._current_image_count = self._last_existing_image_id() + 1

    def is_post_present(self, post_id: str) -> bool:
        return post_id in self.contents_table.index

    def get_post(self, post_id: str) -> tp.Optional[Post]:
        if self.is_post_present:
            post_row = self.contents_table.loc[post_id]
            return Post(
                id=post_id,
                image_url=post_row.image_url,
                caption=post_row.caption,
                comments=post_row.comments.split("\n"),
            )
        return None

    def _rows_to_posts(self, rows) -> tp.List[Post]:
        post_objects = []
        for index, row in rows.iterrows():
            post = Post(
                id=index,
                image_url=row["image_url"],
                caption=row["caption"],
                tags=row["tags"].split(",") if pd.notna(row["tags"]) else [],
                comments=(
                    row["comments"].split("\n") if pd.notna(row["comments"]) else []
                ),
            )
            post.company = row["company"]
            post_objects.append(post)
        return post_objects

    def update_post_info(self, post: Post):
        new_row = {
            "image_url": post.image_url,
            "caption": post.caption,
            "comments": "\n".join(post.comments),
            "number_comments": len(post.comments),
            "company": post.company,
        }
        self.contents_table.loc[post.id] = new_row

    def save_table_changes(self):
        self.contents_table.to_csv(self._table_path)

    def save_image_for_post(self, post_id: str, img: Image):
        # saving image
        image_file_name = self.IMAGE_NAME_FORMAT.format(
            image_id=self._current_image_count
        )
        if img is None:
            logging.info(
                f"Cant's save image for post: {post_id}, it seems it could not be loaded"
            )
        img.save(os.path.join(self.folder_path, image_file_name))
        self._current_image_count += 1

        # updating image file info for post
        try:
            old_file = self.contents_table.loc[post_id, "image_file"]
            if pd.notna(old_file):
                logging.info(f"Attempted replacing image file for post: {post_id}")
            self.contents_table.loc[post_id, "image_file"] = image_file_name
        except KeyError:
            print(f"Tried saving image for unknown post: {post_id}")
            raise

    def get_all_with_no_image(self) -> tp.List[Post]:
        return self._rows_to_posts(
            self.contents_table[self.contents_table["image_file"].isna()]
        )

    def get_all_with_no_comment(self) -> tp.List[Post]:
        return self._rows_to_posts(
            self.contents_table[self.contents_table["comments"].isna()]
        )

    def _clear_old_contents(self):
        content_extentions = ("jpg", "jpeg", "png", "gif", "bmp", "csv")
        if os.path.exists(self.folder_path):
            for file_name in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, file_name)
                try:
                    if os.path.isfile(file_path) and file_name.lower().endswith(
                        content_extentions
                    ):
                        os.unlink(file_path)
                except Exception:
                    print(f"Error clearing {file_path}")
                    raise
            print(f"Contents of {self.folder_path} cleared.")

    def _last_existing_image_id(self):
        if os.path.exists(self.folder_path):
            for entry in os.scandir(self.folder_path):
                if not entry.is_file():
                    pass
                match = self.IMAGE_NAME_REGEX.match(entry.name)
                if match:
                    return int(match.group(1))
        return -1
