import re
import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup

from config import LOGIN_URL, RESERVATIONS_URL

load_dotenv()

DEBUG = os.environ.get("DEBUG", False)

def get_session():
    session = requests.Session()
    username = os.environ.get("MYTURN_USERNAME")
    if not username:
        raise "Set the MYTURN_USERNAME env var!"

    password = os.environ.get("MYTURN_PASSWORD")
    if not password:
        raise "Set the MYTURN_PASSWORD env var!"

    login_payload = {
        'j_username': username,
        'j_password': password,
        '_spring_security_remember_me': 'on'
    }

    response = session.post(LOGIN_URL, data=login_payload)

    # Check login was successful
    if response.ok:
        print("Logged in!")
    else:
        raise f"Failed to log in. Status code: {response.status_code}"

    return session


def get_reservations_page():
    if DEBUG:
        with open('example.html', 'r') as file:
            example = file.read()
        return BeautifulSoup(example, 'html.parser')
    else:
        session = get_session()
        response = session.get(RESERVATIONS_URL)
        return BeautifulSoup(response.text, 'html.parser')


def get_reservations():
    reservations = {}

    soup = get_reservations_page()

    for res in soup.find_all("div", class_="panel reservation"):
        user_info = res.find("span", id=re.compile(r"username-reservation-\d+"))
        user_id = re.search(r"userId=(\d+)", user_info.a.attrs["href"])[1]
        user_name = user_info.a.text

        reservation_items = []

        for item in res.table.tbody.find_all("tr"):
            values = [col.text.strip() for col in item.find_all("td")]
            reservation_items.append({
                "id": values[1],
                "name": values[2],
                "location": values[3]
            })

        if user_id in reservations.keys():
            reservations[user_id]["items"] = reservations[user_id]["items"] + reservation_items
        else:
            reservations[user_id] = {
                "user_name": user_name,
                "items": reservation_items
            }

    return reservations



for user_id, user in get_reservations().items():

    print(f"{user['user_name']}")
    print("-------------------------------")
    for item in user["items"]:
        print(f"{item['id']} {item['location']} {item['name']}")
    print("\r")
    print("\r")

