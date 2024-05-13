# Instagram-scraper
Small console app for scraping images and comments from instagram by tags.

## Setup
Create and activate Virtual Environment (Recommended)
```bash
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
```
Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

The configuration is done via environment variables or command line arguments.
The environment variables are loaded from a `.env` file in the root directory of the project.
The command line arguments override the environment variables.

Also before running the app make sure to provide `companies.json` file that contains dictionary where keys are company names and values - list of reevant tags. You can add your own, but make sure they exist.

The following configuration options are available:

- `SCRAPER_OUTPUT_PATH`: The absolute path to the directory where all files will be stored. (default: `./output`)
- `INSTAGRAM_LOGIN`: The Instagram login for authorization. (required for scraping comments)
- `INSTAGRAM_PASSWORD`: The Instagram password for authorization. (required for scraping comments)
- `SCRAPE_POSTS`: Whether to scrape posts. If on, firstly the general posts by tags will be scraped and stored in content.csv. Else, the future scraping will be applied to all empty fields found in the table. (default: `True`)
- `SCRAPE_IMAGES`: Whether to scrape images. If on, the authorization is recomended. (default: `False`)
- `SCRAPE_COMMENTS`: Whether to scrape comments. (default: `False`)
- `COMPANIES`: A list of company names that are being scraped. They are expected to be keys in companies.json that lies in the root. If none provided, will use ALL comapnies found in the file. (default: all companies in `companies.json`)

## Usage
usage:
```bash
instagram_scraper.py [-h] [–instagram-login INSTAGRAM_LOGIN] [–instagram-password INSTAGRAM_PASSWORD] [–output-path OUTPUT_PATH] [–scrape-posts] [–scrape-images] [–scrape-comments] [–companies COMPANIES [COMPANIES …]]
```
Notice: if you're in Russia use VPN.
### Example
```bash
python instagram_scraper.py –-scrape-posts –-scrape-images –-scrape-comments –-companies netflix yota –-output-path output
```

This will scrape posts, images, and comments for the companies `netflix` and `yota`. The results will be stored in the `output` directory.