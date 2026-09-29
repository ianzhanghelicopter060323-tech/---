import json
import re
import requests
import datetime
from bs4 import BeautifulSoup
import os


"""
爬取数据：
    总的来说的原理：本质上是向服务器发出http请求，服务器返回html后，
    程序脚本根据html的标签分析需要的信息并返回

    请求头与网址设定：headers 是一个 Python 字典，用于设置 HTTP 请求头。
    请求头是随请求发送给服务器的附加信息，其中 User-Agent 用于描述发起请求的客户端。
    请求头会随请求信息一并发给网页服务器
"""
def craw_wiki_data() :
    # 请求头
    # 本机为 ubuntu 但 windows 本身表示兼容标志，和实际系统无关
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 百度百科《乘风破浪的姐姐》url
    url = 'http://127.0.0.1:5000'

    # try:
        # 向服务器发起请求，返回html文本
    respond = requests.get(url, headers=headers)
    print(respond)
    #except:

