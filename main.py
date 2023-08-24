# Made by chareou (roblox) lovingsosa (discord)

try:
    import os
    import requests
    import json
    import time
    import colorama
    from colorama import init
    import traceback
    import threading
    import random
except ImportError:
    os.system("pip install requests colorama")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json; charset=utf-8",
}

init(autoreset=True)

config = json.load(open("config.json", "r"))


class Snipe:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.ready = False
        self.only_new = config["misc"]["only_new"]
        self.accounts = {
            config["accounts"]["main_account"][-4:]: {
                "name": None,
                "id": 0,
                "cookie": config["accounts"]["main_account"],
                "auth": None,
                "owned": [],
            }
        }

        for cookie in config["accounts"]["alt_accounts"]:
            if cookie:
                self.accounts[cookie[-4:]] = {
                    "cookie": cookie,
                    "auth": None,
                    "name": None,
                    "id": 0,
                    "owned": [],
                }
        self.verify_cookies()
        threading.Thread(target=self.auto_updater).start()

        while not self.ready:
            time.sleep(1)

        print(colorama.Fore.GREEN + "Successfully started")

        if config["webhook"]["enabled"]:
            self.webhook_url = config["webhook"]["url"]

        if config["misc"]["bundles"]:
            threading.Thread(target=self.get_free_bundles).start()

    def verify_cookies(self):
        for cookie, details in self.accounts.items():
            try:
                response = self.session.get(
                    "https://www.roblox.com/my/settings/json",
                    headers={"Cookie": f'.ROBLOSECURITY={details["cookie"]}'},
                )
                if response.status_code == 200:
                    json_response = response.json()
                    self.accounts[cookie]["id"] = json_response.get("UserId")
                    self.accounts[cookie]["name"] = json_response.get("Name")
                else:
                    raise Exception

            except Exception:
                input(f"> Invalid cookie ending in {cookie} ")
                exit(0)

    def send_webhook(self, name, user, _id):
        if config["webhook"]["enabled"]:
            data = {
                "content": None,
                "embeds": [
                    {
                        "title": f"{name}",
                        "description": f"Successfully bought {name} on {user}",
                        "url": f"https://roblox.com/bundles/{_id}",
                        "color": 2829617,
                    }
                ],
                "attachments": [],
            }
            try:
                self.session.post(self.webhook_url, json=data)
            except Exception:
                pass

    def get_owned_bundles(self):
        for account in self.accounts:
            with requests.Session() as session:
                cursor = ""
                while cursor is not None:
                    response = session.get(
                        f'https://catalog.roblox.com/v1/users/{self.accounts[account]["id"]}/bundles/1?limit=100&nextPageCursor=&sortOrder=Desc&cursor={cursor}',
                        headers={
                            "Cookie": f'.ROBLOSECURITY={self.accounts[account]["cookie"]}'
                        },
                    )
                    if response.status_code == 200:
                        json_response = response.json()
                        cursor = json_response["nextPageCursor"]
                        for item in json_response["data"]:
                            if item["id"] not in self.accounts[account]["owned"]:
                                self.accounts[account]["owned"].append(item["id"])

    def fetch_data(self, cursor):
        urls = [
            "https://catalog.roblox.com/v1/search/items?limit=120&category=Characters&sortType=3&maxPrice=0&salesTypeFilter=1",
            "https://catalog.roblox.com/v1/search/items?sortType=3&limit=120&maxPrice=0&category=Characters&salesTypeFilter=1",
            "https://catalog.roblox.com/v1/search/items?salesTypeFilter=1&maxPrice=0&limit=120&category=Characters&sortType=3",
            "https://catalog.roblox.com/v1/search/items?limit=120&sortType=3&category=Characters&salesTypeFilter=1&maxPrice=0",
            "https://catalog.roblox.com/v1/search/items?salesTypeFilter=1&category=Characters&limit=120&maxPrice=0&sortType=3",
            "https://catalog.roblox.com/v1/search/items?maxPrice=0&limit=120&salesTypeFilter=1&category=Characters&sortType=3",
            "https://catalog.roblox.com/v1/search/items?category=Characters&limit=120&sortType=3&maxPrice=0&salesTypeFilter=1",
            "https://catalog.roblox.com/v1/search/items?salesTypeFilter=1&maxPrice=0&limit=120&sortType=3&category=Characters",
            "https://catalog.roblox.com/v1/search/items?salesTypeFilter=1&sortType=3&limit=120&category=Characters&maxPrice=0",
            "https://catalog.roblox.com/v1/search/items?maxPrice=0&sortType=3&limit=120&category=Characters&salesTypeFilter=1",
        ]

        response = self.session.get(
            f"{random.choice(urls)}&cursor={cursor}"
            if cursor is not None
            else random.choice(urls),
            cookies={
                ".ROBLOSECURITY": self.accounts.get(
                    config["accounts"]["main_account"][-4:]
                )["cookie"]
            },
            headers=headers,
        )
        return response

    def get_free_bundles(self):
        current_cursor = ""

        if self.only_new == True:
            while current_cursor is not None:
                response = self.fetch_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            self.accounts[account]["owned"].append(item["id"])

        while True:
            try:
                response = self.fetch_data(current_cursor)
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if item["id"] not in self.accounts[account]["owned"]:
                                extra_info = self.session.get(
                                    f'https://catalog.roblox.com/v1/bundles/{item["id"]}/details',
                                    cookies={
                                        ".ROBLOSECURITY": config["accounts"][
                                            "main_account"
                                        ][-4:]
                                    },
                                )
                                if extra_info.status_code == 200:
                                    extra_json = extra_info.json()
                                    self.buy(
                                        extra_json["product"]["id"],
                                        extra_json["creator"]["id"],
                                        account,
                                        extra_json["id"],
                                        extra_json["name"],
                                    )
                                    time.sleep(1)
                time.sleep(2)
            except Exception as error:
                print(f"{colorama.Fore.RED}Error in \n {traceback.format_exc()}")

    def refresh_cookies(self):
        for cookie, details in self.accounts.items():
            try:
                response = self.session.post(
                    "https://friends.roblox.com/v1/users/1/request-friendship",
                    headers={"Cookie": f'.ROBLOSECURITY={details["cookie"]}'},
                )
                if response.headers.get("x-csrf-token"):
                    self.accounts[cookie]["auth"] = response.headers["x-csrf-token"]
                else:
                    raise Exception

            except Exception:
                input(f"> Invalid cookie ending in {cookie}")
                exit(0)

    def auto_updater(self):
        self.get_owned_bundles()
        while True:
            self.refresh_cookies()
            self.ready = True
            time.sleep(240)

    def buy(self, productid, sellerid, account, id_, name):
        payload = {
            "expectedCurrency": 1,
            "expectedPrice": 0,
            "expectedSellerId": sellerid,
        }

        buy_headers = headers.copy()
        buy_headers["x-csrf-token"] = self.accounts[account]["auth"]
        while True:
            try:
                response = self.session.post(
                    f"https://economy.roblox.com/v1/purchases/products/{productid}",
                    json=payload,
                    cookies={".ROBLOSECURITY": self.accounts[account]["cookie"]},
                    headers=buy_headers,
                )
                if response.status_code == 200:
                    status = response.json().get("statusCode", 690)
                    if status == 500:
                        print(
                            colorama.Fore.YELLOW
                            + f"> Something went wrong: {response.json()['errorMsg']}"
                        )
                        if response.json()["errorMsg"] == "You already own this item.":
                            self.accounts[account]["owned"].append(id_)
                            break
                    elif status == 690:
                        print(
                            colorama.Fore.GREEN
                            + f"> Successfully bought (character) {name} on {self.accounts[account]['name']}"
                        )
                        self.accounts[account]["owned"].append(id_)
                        threading.Thread(
                            target=self.send_webhook,
                            args=(name, self.accounts[account]["name"], id_),
                        ).start()
                        break
                    else:
                        break
                elif response.status_code == 403:
                    if "Too many requests" in response.text:
                        print(
                            colorama.Fore.YELLOW
                            + f"> Waiting a minute to buy {name} on {self.accounts[account]['name']}"
                        )
                    else:
                        if "Token Validation Failed" in response.text:
                            print(colorama.Fore.YELLOW + "> Refreshing auth token")
                            self.refresh_cookies()
                time.sleep(60)
            except Exception:
                print(f"{colorama.Fore.RED}> Error in \n {traceback.format_exc()}")


if __name__ == "__main__":
    Snipe()
