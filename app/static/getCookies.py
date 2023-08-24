import requests
session = requests.Session()
header = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}
url = 'https://www.zhibo8.cc'
response = session.get(url)
cookies = session.cookies.get_dict()
print(cookies)
