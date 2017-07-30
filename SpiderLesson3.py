# coding: utf-8
"""
爬虫课练习代码
课程作业-爬虫入门03-爬虫基础-WilliamZeng-20170716
"""

import os
import time
import urllib2
import urlparse
from bs4 import BeautifulSoup  # 用于解析网页中文, 安装:pip install beautifulsoup4.
# Windows环境下需要在命令行模式里并在安装pip的目录下运行,比如D:\Python27\Scripts.
# PyCharm可以直接在Project Interpretr界面安装各种package.


def download(url, retry=2):
    """
    下载页面的函数，会下载完整的页面信息
    :param url: 要下载的url
    :param retry: 重试次数
    :return: 原生html
    """
    print "downloading: ", url
    # 设置header信息，模拟浏览器请求
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    try: #爬取可能会失败，采用try-except方式来捕获处理
        request = urllib2.Request(url, headers=header) #设置请求数据
        html = urllib2.urlopen(request).read() #抓取url
    except urllib2.URLError as e: #异常处理
        print "download error: ", e.reason
        html = None
        if retry > 0: #未超过重试次数，可以继续爬取
            if hasattr(e, 'code') and 500 <= e.code < 600: #错误码范围，是请求出错才继续重试爬取
                print e.code
                return download(url, retry - 1)
    time.sleep(1) #等待1s，避免对服务器造成压力，也避免被服务器屏蔽爬取
    return html

def crawled_links(url_seed, url_root):
    """
    抓取文章链接
    :param url_seed: 下载的种子页面地址
    :param url_root: 爬取网站的根目录
    :return: 需要爬取的页面
    """
    crawled_url = set()  # 需要爬取的页面
    i = 1
    flag = True #标记是否需要继续爬取
    while flag:
        url = url_seed % i #真正爬取的页面
        i += 1 #下一次需要爬取的页面

        html = download(url) #下载页面
        if html == None: #下载页面为空，表示已爬取到最后
            break

        soup = BeautifulSoup(html, "html.parser") #格式化爬取的页面数据
        links = soup.find_all('a', {'class': 'title'}) #获取标题元素
        if links.__len__() == 0: #爬取的页面中已无有效数据，终止爬取
            flag = False

        for link in links: #获取有效的文章地址
            link = link.get('href')
            if link not in crawled_url:
                realUrl = urlparse.urljoin(url_root, link)
                crawled_url.add(realUrl)  # 记录未重复的需要爬取的页面
            else:
                print 'end'
                flag = False  # 结束抓取

    paper_num = crawled_url.__len__()
    print 'total paper num: ', paper_num
    return crawled_url

def crawled_page(crawled_url):
    """
    爬取文章内容
    :param crawled_url: 需要爬取的页面地址集合
    """
    for link in crawled_url: #按地址逐篇文章爬取
        html = download(link)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('h1', {'class': 'title'}).text #获取文章标题
        content = soup.find('div', {'class': 'show-content'}).text #获取文章内容

        if os.path.exists('spider_res/') == False: #检查保存文件的地址
            os.mkdir('spider_res')

        file_name = 'spider_res/' + title + '.txt' #设置要保存的文件名
        if os.path.exists(file_name):
            # os.remove(file_name) # 删除文件
            continue  # 已存在的文件不再写
        file = open('spider_res/' + title + '.txt', 'wb') #写文件
        content = unicode(content).encode('utf-8', errors='ignore')
        file.write(content)
        file.close()

download('http://www.jianshu.com/p/10b429fd9c4d')