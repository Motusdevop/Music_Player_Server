import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))

BOT_TOKEN = os.environ['BOT_TOKEN']

MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET = 1
MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET = 1
