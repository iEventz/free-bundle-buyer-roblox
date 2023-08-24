<p align="left"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/iEventz/free-bundle-buyer-roblox?color=yellow&style=flat-square"> <img alt="GitHub forks" src="https://img.shields.io/github/forks/iEventz/free-bundle-buyer-roblox?style=flat-square"></p>

<h1 align="left">Free Roblox Bundle Buyer</h1>

<p align="left">Automatically buys new or previously free bundles in the Roblox catalog.</p>

### Usage
Update the json with all your settings
```json
{
    "accounts": {
        "main_account": "",
        "alt_accounts": []
    },
    "webhook": {
        "enabled": true,
        "url": ""
    },
    "misc": {
        "bundles": true,
        "only_new": false
    }
}
```
#### accounts
Add your accounts in here and your alts

#### webhook
Notifies you when there has been a successfull purchase

#### bundles
Toggle enabled or false depending on if you want to buy free bundles (heads coming soon)

#### only new
False to catch up on previous free bundles true to only buy the new ones in the catalog
