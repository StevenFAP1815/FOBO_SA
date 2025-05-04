import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv(override=True)
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["MY_NUMBER"] = os.getenv("MY_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["TEST_NUMBER_META"] = os.getenv("TEST_NUMBER_META")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["TEST_NUMBER_ID"] = os.getenv("TEST_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    app.config["ID_WHATSAPP_BUSSINES"] = os.getenv("ID_WHATSAPP_BUSSINES")
    app.config["ACCESS_TOKEN_CHECK"] = os.getenv("ACCESS_TOKEN_CHECK")
    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    app.config["OPENAI_ASSISTANT_ID"] = os.getenv("OPENAI_ASSISTANT_ID")

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )