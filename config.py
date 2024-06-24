import dotenv
import os
import json
from datetime import datetime, timedelta

dotenv.load_dotenv()

BOT_TOKEN = (os.getenv('token'))

USERS = (os.getenv('users'))

today = datetime.now() + timedelta(days=0)