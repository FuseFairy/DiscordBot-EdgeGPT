import requests
import asyncio
import time
import json
import os
from datetime import datetime

async def refresh_cookies():
    while True:
        cookies, expirationDate = fetch_cookies_from_bing()  # Fetch cookies and expiration date
        if os.getenv("BING_COOKIES"):
            os.environ["BING_COOKIES"] = cookies
        else:
            with open("cookies.json", "w") as file:
                json.dump(cookies, file, indent=4)
        await asyncio.sleep(expirationDate)

def fetch_cookies_from_bing():
    target_url = 'https://bing.com'

    session = requests.Session()
    response = session.get(target_url)

    cookies = session.cookies.get_dict()  # Get cookies from the session

    formatted_cookies = []
    expirationDate = None
    for name, value in cookies.items():
        # Extract expiration date if available
        if 'expires' in response.headers.get('Set-Cookie', ''):
            expires_str = response.headers['Set-Cookie'].split('expires=')[1].split(';')[0]
            expirationDate = int(time.mktime(datetime.strptime(expires_str, '%a, %d-%b-%Y %H:%M:%S %Z').timetuple()))
        cookie = {
            "name": name,
            "value": value,
            "domain": ".bing.com",
            "hostOnly": False,
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "sameSite": "no_restriction",
            "session": False,
            "firstPartyDomain": "",
            "partitionKey": None,
            "expirationDate": expirationDate,
            "storeId": None
        }
        formatted_cookies.append(cookie)

    with open('cookies.json', 'w') as f:
        json.dump(formatted_cookies, f, indent=4)

    return formatted_cookies, expirationDate