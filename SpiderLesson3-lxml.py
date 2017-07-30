# coding: utf-8
"""
爬虫课练习代码
课程作业-爬虫入门03-爬虫基础-WilliamZeng-20170716
"""

import os
import time
import urllib2
import urlparse
from bs4 import BeautifulSoup
"""
用于解析网页中文, 安装:pip install beautifulsoup4.Windows环境下需要在命令行模式里并在安装pip的目录下运行,比如D:\Python27\Scripts.PyCharm可以直接在Project Interpretr界面安装各种package.
"""

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

def crawl_article_images(post_url):
    """
    抓取文章中图片链接
    :param post_url: 文章页面
    """
    image_url = set()  # 爬取的图片链接
    flag = True # 标记是否需要继续爬取
    while flag:
        html = download(post_url) # 下载页面
        if html == None:
            break

        soup = BeautifulSoup(html, "html.parser") # 格式化爬取的页面数据
        title = soup.find('h1', {'class': 'title'}).text  # 获取文章标题
        image_div = soup.find_all('div', {'class': 'image-package'}) # 获取文章图片div元素
        if image_div.__len__() == 0: # 爬取的页面中无图片div元素，终止爬取
            break

        i = 1
        image_content = ''
        for image in image_div:
            image_link = image.img.get('data-original-src') # 获取图片的原始链接
            image_caption = image.find('div', {'class': 'image-caption'}).text # 获取图片的标题
            image_content += str(i) + '. ' + (unicode(image_caption).encode('utf-8', errors='ignore')) + ' : '+ (unicode(image_link).encode('utf-8', errors='ignore')) + '\n'
            image_url.add(image_link)  # 记录未重复的爬取的图片链接
            i += 1

        if os.path.exists('spider_output/') == False:  # 检查保存文件的地址
            os.mkdir('spider_output')

        file_name = 'spider_output/' + title + '_images.txt'  # 设置要保存的文件名
        if os.path.exists(file_name) == False:
            file = open('spider_output/' + title + '_images.txt', 'wb')  # 写文件
            file.write(image_content)
            file.close()
        flag = False

    image_num = image_url.__len__()
    print 'total number of images in the article: ', image_num

def crawl_article_text_link(post_url):
    """
    抓取文章中的文字链接
    :param post_url: 文章页面
    """
    text_link_url = set()  # 爬取的文字链接
    flag = True # 标记是否需要继续爬取
    while flag:
        html = download(post_url) # 下载页面
        if html == None:
            break

        soup = BeautifulSoup(html, "html.parser") # 格式化爬取的页面数据
        title = soup.find('h1', {'class': 'title'}).text  # 获取文章标题
        article_content = soup.find('div', {'class': 'show-content'}) # 获取文章的内容div
        text_links = article_content.find_all('a', {'target': '_blank'})
        if text_links.__len__() == 0: # 爬取的页面中无图片div元素，终止爬取
            break

        i = 1
        text_links_content = ''
        for link in text_links:
            link_url = link.get('href') # 获取文字链的链接
            link_label = link.text # 获取文字链的文本内容
            text_links_content += str(i) + '. ' + (unicode(link_label).encode('utf-8', errors='ignore')) + ' : '+ (unicode(link_url).encode('utf-8', errors='ignore')) + '\n'
            text_link_url.add(link_url)  # 记录未重复的爬取的文字链的链接
            i += 1

        if os.path.exists('spider_output/') == False:  # 检查保存文件的地址
            os.mkdir('spider_output')

        file_name = 'spider_output/' + title + '_article_text_links.txt'  # 设置要保存的文件名
        if os.path.exists(file_name) == False:
            file = open('spider_output/' + title + '_article_text_links.txt', 'wb')  # 写文件
            file.write(text_links_content)
            file.close()
        flag = False

    link_num = text_link_url.__len__()
    print 'total number of text links in the article: ', link_num

def crawl_page(crawled_url):
    """
    爬取文章内容
    :param crawled_url: 需要爬取的页面地址集合
    """
    for link in crawled_url: #按地址逐篇文章爬取
        html = download(link)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find('h1', {'class': 'title'}).text #获取文章标题
        content = soup.find('div', {'class': 'show-content'}).text #获取文章内容

        if os.path.exists('spider_output/') == False: #检查保存文件的地址
            os.mkdir('spider_output/')

        file_name = 'spider_output/' + title + '.txt' #设置要保存的文件名
        if os.path.exists(file_name):
            # os.remove(file_name) # 删除文件
            continue  # 已存在的文件不再写
        file = open('spider_output/' + title + '.txt', 'wb') #写文件
        content = unicode(content).encode('utf-8', errors='ignore')
        file.write(content)
        file.close()

crawl_article_images('http://www.jianshu.com/p/10b429fd9c4d')
crawl_article_images('http://www.jianshu.com/p/faf2f4107b9b')
crawl_article_images('http://www.jianshu.com/p/111')
crawl_article_text_link('http://www.jianshu.com/p/10b429fd9c4d')
crawl_article_text_link('http://www.jianshu.com/p/faf2f4107b9b')
crawl_page(['http://www.jianshu.com/p/10b429fd9c4d'])
crawl_page(['http://www.jianshu.com/p/faf2f4107b9b'])