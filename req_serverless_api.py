import requests
from requests.auth import HTTPBasicAuth

"""
application/x-www-form-urlencoded Content-Type is use 'data' parameter value to requests()
application/json Content-Type is use 'json' parameter value to requests()
"""

def request_method(auth, url, payload, method="get"):
    req = ""

    if method == "post":  # 將請求的資料放在request.body, 檔案傳遞會使用到 multi-part 編碼
        req = requests.post(url, json=payload)
        print("request.body :", req.json())
    elif method == "delete":
        req = requests.delete(url)
        print(req)
    elif method == "put":
        req = requests.put(url, json=payload)
        print("request.body :", req.json())
    elif method == "patch":
        req = requests.put(url, json=payload)
        print("request.body :", req.json())
    elif method == "get":  # 將請求的資料放以Query string加在url後面
        req = requests.get(url)  # , params=payload
        print("Response :", req.text)
    print("req status :", req.__repr__())


def main():
    auth = ""
    url = "https://bph2va71cc.execute-api.ap-northeast-1.amazonaws.com/api/city_s3"  # city
    payload = {"b": "A"}
    method = "get".lower()
    request_method(auth, url, payload, method)


if __name__ == '__main__':
    main()


