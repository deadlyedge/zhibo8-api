# 写一个获取 https://zhibo8.cc 页面内容的方法

import requests

def get_zhibo8_html():
    url = 'https://zhibo8.cc/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text

print(get_zhibo8_html())