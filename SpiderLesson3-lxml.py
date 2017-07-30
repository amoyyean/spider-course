# coding: utf-8
"""
爬虫课练习代码lxml版本
课程作业-爬虫入门03-爬虫基础-WilliamZeng-20170716
"""

import os
import time
import urllib2
import lxml.html # lxml中的HTML返回结果解析模块
import lxml.etree # 为了解决中文乱码而专门引入的lxml模块
import urlparse


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
    image_link = []
    flag = True # 标记是否需要继续爬取
    while flag:
        page = download(post_url) # 下载页面
        if page == None:
            break
        my_parser = lxml.etree.HTMLParser(encoding="utf-8")
        html_content = lxml.etree.HTML(page, parser=my_parser) # 格式化爬取的页面数据
        # html_content = lxml.html.fromstring(page) # 格式化爬取的页面数据,fromstring函数未找到解决中文乱码的办法
        title = html_content.xpath('//h1[@class="title"]/text()')  # 获取文章标题
        image_link = html_content.xpath('//div/img/@data-original-src') # 获取图片的原始链接
        image_caption = html_content.xpath('//div[@class="image-caption"]/text()')
        if image_link.__len__() == 0: # 爬取的页面中无图片div元素，终止爬取
            break

        image_content = ''
        for i in range(image_link.__len__()):
             # 获取图片的标题
            image_content += str(i + 1) + '. ' + (unicode(image_caption[i]).encode('utf-8', errors='ignore')) + ' : '+ image_link[i] + '\n'

        if os.path.exists('spider_output/') == False:  # 检查保存文件的地址
            os.mkdir('spider_output')

        file_name = 'spider_output/' + title[0] + '_images_by_lxml.txt'  # 设置要保存的文件名
        if os.path.exists(file_name) == False:
            file = open('spider_output/' + title[0] + '_images_by_lxml.txt', 'wb')  # 写文件
            file.write(image_content)
            file.close()
        flag = False

    image_num = image_link.__len__()
    print 'total number of images in the article: ', image_num

def crawl_article_text_link(post_url):
    """
    抓取文章中的文字链接
    :param post_url: 文章页面
    """
    flag = True # 标记是否需要继续爬取
    while flag:
        page = download(post_url) # 下载页面
        if page == None:
            break

        my_parser = lxml.etree.HTMLParser(encoding="utf-8")
        html_content = lxml.etree.HTML(page, parser=my_parser)  # 格式化爬取的页面数据
        title = html_content.xpath('//h1[@class="title"]/text()')  # 获取文章标题
        text_links = html_content.xpath('//div[@class="show-content"]//a/@href')
        text_links_label = html_content.xpath('//div[@class="show-content"]//a/text()')
        if text_links.__len__() == 0: # 爬取的页面中无图片div元素，终止爬取
            break

        text_links_content = ''
        for i in range(text_links.__len__()):
            text_links_content += str(i + 1) + '. ' + (unicode(text_links_label[i]).encode('utf-8', errors='ignore')) + ' : '+ text_links[i] + '\n'

        if os.path.exists('spider_output/') == False:  # 检查保存文件的地址
            os.mkdir('spider_output')

        file_name = 'spider_output/' + title[0] + '_article_text_links_by_lxml.txt'  # 设置要保存的文件名
        if os.path.exists(file_name) == False:
            file = open('spider_output/' + title[0] + '_article_text_links_by_lxml.txt', 'wb')  # 写文件
            file.write(text_links_content)
            file.close()
        flag = False

    link_num = text_links.__len__()
    print 'total number of text links in the article: ', link_num

def crawl_page(crawled_url):
    """
    爬取文章内容
    :param crawled_url: 需要爬取的页面地址集合
    """
    for link in crawled_url: #按地址逐篇文章爬取
        page = download(link)
        my_parser = lxml.etree.HTMLParser(encoding="utf-8")
        html_content = lxml.etree.HTML(page, parser=my_parser)
        title = html_content.xpath('//h1[@class="title"]/text()') #获取文章标题
        contents = html_content.xpath('//div[@class="show-content"]//text()') #获取文章内容
        content = ''.join(contents)

        if os.path.exists('spider_output/') == False: #检查保存文件的地址
            os.mkdir('spider_output/')

        file_name = 'spider_output/' + title[0] + '_by_lxml.txt' #设置要保存的文件名
        if os.path.exists(file_name):
            # os.remove(file_name) # 删除文件
            continue  # 已存在的文件不再写
        file = open('spider_output/' + title[0] + '_by_lxml.txt', 'wb') #写文件
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