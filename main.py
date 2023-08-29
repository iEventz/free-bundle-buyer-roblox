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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json; charset=utf-8",
}

init(autoreset=True)

config = json.load(open("config.json", "r"))


class Snipe:
    VERSION = "2.0.3"

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
                "owned_bundles": [],
                "owned_heads": [],
            }
        }

        for cookie in config["accounts"]["alt_accounts"]:
            if cookie:
                self.accounts[cookie[-4:]] = {
                    "name": None,
                    "id": 0,
                    "cookie": cookie,
                    "auth": None,
                    "owned_bundles": [],
                    "owned_heads": [],
                }

        self.verify_cookies()
        threading.Thread(target=self.auto_updater).start()
        threading.Thread(target=self.version_updater).start()

        while not self.ready:
            time.sleep(1)

        print(colorama.Fore.GREEN + "Successfully started")

        if config["webhook"]["enabled"]:
            self.webhook_url = config["webhook"]["url"]

        if config["misc"]["bundles"]:
            threading.Thread(target=self.get_free_bundles).start()

        if config["misc"]["heads"]:
            threading.Thread(target=self.get_free_heads).start()

    def version_updater(self):
        response = self.session.get("https://pastebin.com/raw/nALVgjcz")
        if response.status_code == 200:
            if self.VERSION != response.text:
                print(
                    colorama.Fore.YELLOW
                    + "A new version available update at: https://github.com/iEventz/free-bundle-buyer-roblox"
                )

    def verify_cookies(self):
        for cookie, details in self.accounts.items():
            response = self.session.get(
                "https://users.roblox.com/v1/users/authenticated",
                headers={"Cookie": f'.ROBLOSECURITY={details["cookie"]}'},
            )
            if response.status_code == 200:
                json_response = response.json()
                self.accounts[cookie]["id"] = json_response.get("id")
                self.accounts[cookie]["name"] = json_response.get("name")
            else:
                print(
                    colorama.Fore.RED
                    + f"Invalid cookie or ratelimit try again in a minute {response.text}"
                )
                input()
                exit(0)

    def get_owned(self):
        if config["misc"]["bundles"]:
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
                                if (
                                    item["id"]
                                    not in self.accounts[account]["owned_bundles"]
                                ):
                                    self.accounts[account]["owned_bundles"].append(
                                        item["id"]
                                    )
                        else:
                            time.sleep(2)

        if config["misc"]["heads"]:
            for account in self.accounts:
                with requests.Session() as session:
                    cursor = ""
                    while cursor is not None:
                        response = session.get(
                            f'https://catalog.roblox.com/v1/users/{self.accounts[account]["id"]}/bundles/4?limit=100&nextPageCursor=&sortOrder=Desc&cursor={cursor}',
                            headers={
                                "Cookie": f'.ROBLOSECURITY={self.accounts[account]["cookie"]}'
                            },
                        )
                        if response.status_code == 200:
                            json_response = response.json()
                            cursor = json_response["nextPageCursor"]
                            for item in json_response["data"]:
                                if (
                                    item["id"]
                                    not in self.accounts[account]["owned_heads"]
                                ):
                                    self.accounts[account]["owned_heads"].append(
                                        item["id"]
                                    )
                        else:
                            time.sleep(2)

    def send_webhook(self, name, user, bundle_id):
        if config["webhook"]["enabled"]:
            data = {
                "content": None,
                "embeds": [
                    {
                        "title": f"{name}",
                        "description": f"Successfully bought {name} on {user}",
                        "url": f"https://roblox.com/bundles/{bundle_id}",
                        "color": 2829617,
                        "thumbnail": {"url": None},
                        "footer": {
                            "text": "made by lovingsosa"
                        },  # pls dont remove i need my 2 seconds of fame
                    }
                ],
            }
            try:
                thumbnail = self.session.get(
                    f"https://thumbnails.roblox.com/v1/bundles/thumbnails?bundleIds={bundle_id}&size=150x150&format=Png&isCircular=false"
                )
                if thumbnail.status_code == 200:
                    thumbnail = thumbnail.json()["data"][0]["imageUrl"]
                else:
                    thumbnail = None

                data["embeds"][0]["thumbnail"]["url"] = thumbnail
                self.session.post(self.webhook_url, json=data)
            except Exception:
                pass

    def fetch_data(self, cursor, url):
        try:
            response = self.session.get(
                f"{url}&cursor={cursor}" if cursor is not None else url,
                cookies={
                    ".ROBLOSECURITY": self.accounts.get(
                        config["accounts"]["main_account"][-4:]
                    )["cookie"]
                },
                headers=HEADERS,
            )
            return response
        except:
            return

    def get_free_bundles(self):
        current_cursor = ""

        if self.only_new == True:
            while current_cursor is not None:
                response = self.fetch_data(current_cursor, 'https://catalog.roblox.com/v1/search/items?limit=120&category=Characters&sortType=3&maxPrice=0&salesTypeFilter=1')
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            self.accounts[account]["owned_bundles"].append(item["id"])
                time.sleep(0.5)

        while True:
            try:
                response = self.fetch_data(current_cursor, 'https://catalog.roblox.com/v1/search/items?limit=120&category=Characters&sortType=3&maxPrice=0&salesTypeFilter=1')
                if response is not None and response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (
                                item["id"]
                                not in self.accounts[account]["owned_bundles"]
                            ):
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
                                        "bundle",
                                    )
                                    time.sleep(0.5)
                time.sleep(2)
            except Exception as error:
                print(f"{colorama.Fore.RED}Error in \n {traceback.format_exc()}")

    def get_free_heads(self):
        current_cursor = ""

        if self.only_new == True:
            while current_cursor is not None:
                response = self.fetch_data(current_cursor, 'https://catalog.roblox.com/v2/search/items/details?sortType=3&category=BodyParts&limit=120&maxPrice=0&salesTypeFilter=1')
                if response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (
                                item["id"] not in self.accounts[account]["owned_heads"]
                                and item.get("itemType") == "Bundle"
                                and item.get("bundleType") == 4
                            ):
                                self.accounts[account]["owned_heads"].append(item["id"])
                time.sleep(0.5)

        while True:
            try:
                response = self.fetch_data(current_cursor, 'https://catalog.roblox.com/v2/search/items/details?sortType=3&category=BodyParts&limit=120&maxPrice=0&salesTypeFilter=1')
                if response is not None and response.status_code == 200:
                    json_response = response.json()
                    current_cursor = json_response["nextPageCursor"]
                    for item in json_response["data"]:
                        for account in self.accounts:
                            if (
                                item["id"] not in self.accounts[account]["owned_heads"]
                                and item.get("itemType") == "Bundle"
                                and item.get("bundleType") == 4
                            ):
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
                                        "head",
                                    )
                                    time.sleep(0.5)
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
                input(f"> 2 Invalid cookie ending in {cookie}")
                exit(0)

    def auto_updater(self):
        self.get_owned()
        while True:
            self.refresh_cookies()
            self.ready = True
            time.sleep(240)

    def buy(self, productid, sellerid, account, id_, name, type_):
        payload = {
            "expectedCurrency": 1,
            "expectedPrice": 0,
            "expectedSellerId": sellerid,
        }

        buy_headers = HEADERS.copy()
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
                            if type_ == "bundle":
                                self.accounts[account]["owned_bundles"].append(id_)
                            else:
                                self.accounts[account]["owned_heads"].append(id_)
                            break
                        elif response.json()["errorMsg"] == "This item has changed price. Please try again.":
                            if type_ == "bundle":
                                self.accounts[account]["owned_bundles"].append(id_)
                            else:
                                self.accounts[account]["owned_heads"].append(id_)
                            break
                    elif status == 690:
                        print(
                            colorama.Fore.GREEN
                            + f"> Successfully bought ({type_}) {name} on {self.accounts[account]['name']}"
                        )
                        if type_ == "bundle":
                            self.accounts[account]["owned_bundles"].append(id_)
                        else:
                            self.accounts[account]["owned_heads"].append(id_)
                        threading.Thread(
                            target=self.send_webhook,
                            args=(
                                name,
                                self.accounts[account]["name"],
                                id_,
                            ),
                        ).start()
                        break
                    else:
                        break
                elif response.status_code == 429:
                    if "Too many requests" in response.text:
                        print(
                            colorama.Fore.YELLOW
                            + f"> Waiting a minute to buy {name} on {self.accounts[account]['name']}"
                        )
                        time.sleep(60)
                elif response.status_code == 403:
                    if "Token Validation Failed" in response.text:
                        print(colorama.Fore.YELLOW + "> Refreshing auth token")
                        self.refresh_cookies()
                        buy_headers["x-csrf-token"] = self.accounts[account]["auth"]
                        time.sleep(1)
            except Exception:
                print(f"{colorama.Fore.RED}> Error in \n {traceback.format_exc()}")


if __name__ == "__main__":
    Snipe()
