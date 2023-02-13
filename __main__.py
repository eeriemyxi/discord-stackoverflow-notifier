#!python

import json
import logging
import time

import httpx
import yaml
import yarl
from yarl import URL
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


logging.info("Checking whether 'last_checked' file exists or not.")
try:
    with open("last_checked", "r") as file:
        logging.info("'last_checked' file exists.")
        last_checked = int(file.read())
        logging.info("Last checked time is: %s", last_checked)
except FileNotFoundError:
    logging.warning("'last_checked' file does not exist. Creating one...")
    with open("last_checked", "w") as file:
        unix_time = int(time.time())
        logging.info("UNIX time for 'last_checked' file is: %s", unix_time)
        file.write(str(unix_time))
        logging.info("'last_checked' file has been sucessfully created.")
        last_checked = unix_time


with open("config.yml", "r") as file:
    config = file.read()
    logging.info("Config file has been read: %s", config)
    CONFIG: dict = yaml.safe_load(config)

DISCORD_API_BASE_URL = yarl.URL("discord.com/api")
STACKOVERFLOW_BASE_URL = yarl.URL("api.stackexchange.com")
STACKOVERFLOW_API_VERSION = 2.3


def search_stackexchange(**kwargs):
    """Sends GET request to a built search URL of StackExchange
    as per the given queries as keyword arguments"""
    logging.info("Searching for questions with provided keyword arguments: %s", kwargs)
    built_url = str(
        URL.build(
            scheme="https",
            host=str(
                STACKOVERFLOW_BASE_URL / str(STACKOVERFLOW_API_VERSION) / "questions"
            ),
            query=kwargs,
        )
    )
    logging.info("Search URL has been successfully built: %s", built_url)
    return httpx.get(built_url)


search_request = search_stackexchange(
    fromdate=last_checked,
    order=CONFIG["STACKOVERFLOW"]["order"],
    sort=CONFIG["STACKOVERFLOW"]["sort"],
    tagged=CONFIG["STACKOVERFLOW"]["tagged"],
    site=CONFIG["STACKOVERFLOW"]["site"],
)
search_result = search_request.json()
logging.info("Search result has been successfully retrieved: %s", search_result)

logging.info("Building URL to execute Discord webhook...")
webhook_execute_URL = URL.build(scheme="https", host=str(DISCORD_API_BASE_URL / "webhooks" / str(CONFIG['WEBHOOK_ID']) / CONFIG['WEBHOOK_TOKEN']))
logging.info("URL to execute Discord webhook has been parsed: %s", webhook_execute_URL)
stringified_json = json.dumps(CONFIG["MESSAGE_FORM_DATA"])
logging.info("Converted message object to string: %s", stringified_json)

logging.info("Checking for new posts...")
for post in reversed(search_result["items"]):
    logging.info("New post has been found with following attributes: %s", post)

    owner = post["owner"]
    post["tags"] = ", ".join(post["tags"])
    owner["author_link"] = owner["link"]
    del owner["link"]
    del post["owner"]
    kwargs = post | owner
    logging.info("Keywords for formatting has been parsed: %s", kwargs)

    message_object = json.loads(stringified_json % kwargs)
    logging.info(
        "Message object to pass to the webhook execute URL has been parsed: %s",
        message_object,
    )

    message_post_request = httpx.post(
        str(webhook_execute_URL),
        json=message_object,
    )
    logging.info(
        "POST request has been sent and the status code is: %s", message_post_request.status_code
    )
    logging.info("Waiting for five seconds before checking for other items...")
    time.sleep(5)
else:
    logging.info("No new/other posts found.")

logging.info("Checking finished.")
unix_time = str(int(time.time()))
logging.info("Updating 'last_checked' file to: %s", unix_time)
with open("last_checked", "w") as file:
    file.write(unix_time)
