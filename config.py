import dotenv
import os
import json
from datetime import datetime, timedelta
from icecream import ic

dotenv.load_dotenv()


BOT_TOKEN = (os.getenv('token'))

USERS = (os.getenv('users'))

ADMIN = (os.getenv('admin'))

today = datetime.now() + timedelta(days=0)

with open('cookies.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)
tmp_cookies = []
for cookie in cookies:
    listik = ['expirationDate', 'hostOnly', 'session', 'sameSite', 'storeId', 'httpOnly']
    for i in listik:
        if i in cookie.keys():
            del cookie[i]
    tmp_cookies.append(cookie)
cookies = tmp_cookies