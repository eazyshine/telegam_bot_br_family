# Load all environment variables from .env file
from environs import Env

env = Env()
env.read_env()

# Telegram bot credentials
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_IDS = env.list("ADMIN_IDS", subcast=int)  # comma-separated list of admin Telegram IDs

# MySQL connection settings
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_NAME = env.str("DB_NAME")
