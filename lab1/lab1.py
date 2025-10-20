import requests
import json

# exercise 1

url1 = "https://scd.dfilip.xyz/lab1/task1"
check1 = "https://scd.dfilip.xyz/lab1/task1/check"

params1 = {
    "nume": "Andrei-Gabriel Radu",
    "grupa": "342C3",
}

data1 = {
    "secret": "SCDisNice"
}

headers1 = {
    "secret2": "SCDisBest"
}

r1 = requests.post(url1, params=params1, data=data1, headers=headers1, timeout=10)

print(r1.json())

r1_check = requests.post(check1, params=params1, data=data1, headers=headers1, timeout=10)
with open("task1.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(r1_check.json(), ensure_ascii=False, indent=2))

# exercise 2

url2 = "https://scd.dfilip.xyz/lab1/task2"

params2 = {
    "username": "scd", 
    "password": "admin", 
    "nume": "Andrei-Gabriel Radu",
}

r2 = requests.post(url2, json=params2, timeout=10)

print(r2.json())

with open("task2.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(r2.json(), ensure_ascii=False, indent=2))

# exercise 3

login_url = "https://scd.dfilip.xyz/lab1/task3/login"
check_url = "https://scd.dfilip.xyz/lab1/task3/check"

params3 = {
    "username": "scd", 
    "password": "admin", 
    "nume": "Andrei-Gabriel Radu",
}

with requests.Session() as s:
    r3_login = s.post(login_url, json=params3, timeout=10, allow_redirects=True)

    ct = r3_login.headers.get("Content-Type", "")
    if "application/json" in ct:
        print(r3_login.json())
    else:
        print(f"Login status: {r3_login.status_code}, cookies: {len(s.cookies)}")

    r3_check = s.get(check_url, timeout=10)
    print(r3_check.text)

    with open("task3_check.txt", "w", encoding="utf-8") as f:
        f.write(r3_check.text)
