import re
import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup

from config import LOGIN_URL, RESERVATIONS_URL, LOANS_URL, SEARCH_USERS_URL

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

session = get_session()

def get_reservations_page():
    # if DEBUG:
    #     with open('example.html', 'r') as file:
    #         example = file.read()
    #     return BeautifulSoup(example, 'html.parser')
    # else:
    response = session.get(RESERVATIONS_URL)
    return BeautifulSoup(response.text, 'html.parser')


def get_reservations():
    reservations = {}

    soup = get_reservations_page()

    for res in soup.find_all("div", class_="panel reservation"):
        user_info = res.find("span", id=re.compile(r"username-reservation-\d+"))
        user_id = re.search(r"userId=(\d+)", user_info.a.attrs["href"])[1]
        # membership_id = re.search(r"\((\d+)\)$", user_info.a.text)[1]
        user_name = user_info.a.text

        reservation_items = []

        for item in res.table.tbody.find_all("tr"):
            # Check if its warning us about duplicates.
            renewal = False
            warning = False
            currently_out_to = {}
            cols = item.find_all("td")
            if item.find_all("span", class_="badge-warning"):
                warning = True
                item_link = cols[1].find_all("a")[0]
                item_id = re.search(r"show/(\d+)", item_link.attrs["href"])[1]

                response = session.post(LOANS_URL, data={
                    "item.id": item_id,
                    "includeProjectData": "false",
                    "brief": "true",
                    "out": "true",
                })
                other_loan_user_id = str(response.json()["data"][0]["user"]["id"])
                other_loan_username = str(response.json()["data"][0]["user"]["username"])
                renewal = user_id == other_loan_user_id

                if not renewal:
                    # look up the current users phone number etc
                    response = session.post(SEARCH_USERS_URL, data={
                        "username": other_loan_username,
                        "exportField[0]": "membership.attributes.membershipId",
                        "exportField[1]": "firstName",
                        "exportField[2]": "lastName",
                        "exportField[3]": "emailAddress",
                        "exportField[4]": "address.phone",
                        "exportField[5]": "address.phone2",
                    })
                    currently_out_to = response.json()['data'][0]

            reservation_items.append({
                "id": cols[0].text.strip(),
                "name": cols[1].find_all("a")[0].text.strip(),
                "location": cols[2].text.strip(),
                "renewal": renewal,
                "warning": warning,
                "currently_out_to": currently_out_to,
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
        line = f"{item['id']} \t {item['location']} \t {item['name']}"
        if item["renewal"]:
            line = "[RENEWAL] " + line

        if item["currently_out_to"]:
            print(line + "*")
            print(f"\t\t\t\t\t*Currently out to {item['currently_out_to']['displayName']} ({item['currently_out_to']['phone']})\r")
        else:
            print(line)

    print("\r")
    print("\r")

