import requests

def safe_request_get(url, timeout=15, headers=None):
    try:
        return requests.get(url, timeout=timeout, headers=headers or {"User-Agent": "hicore-bot/1.0"})
    except Exception as e:
        print("HTTP GET failed:", url, e)
        return None
