from db import BotDB
from dotenv import load_dotenv,find_dotenv
from config import *
load_dotenv(find_dotenv())
BotDB = BotDB(os.getenv('DB_URI'))