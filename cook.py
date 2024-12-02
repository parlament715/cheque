import json
print("Cooking is start ...")
json_keys = ["domain", "expirationDate", "hostOnly", "httpOnly",
             "name", "path", "sameSite", "secure", "session", "storeId", "value"]
with open("cookies.json", "r") as f:
    cookie_json = json.load(f)
for cookie in cookie_json:
    keys = list(cookie.keys())
    for key in keys[:]:
        if key not in json_keys:
            del cookie[key]
with open('cookies.json', 'w') as f:
    json.dump(cookie_json, f, indent=2, ensure_ascii=False)
print("Cookies is cooked!!!")
