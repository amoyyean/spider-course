# coding: utf-8
"""
爬虫课练习代码
课程作业-爬虫入门04-构建爬虫-WilliamZeng-20170729
"""

import os
import time
import urllib2
from bs4 import BeautifulSoup
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

def crawl_list(url):
    """
    爬取文章列表
    :param url 下载的种子页面地址
    :return:
    """
    html = download(url) #下载页面
    if html == None:  # 下载页面为空，表示已爬取到最后
        return

    soup = BeautifulSoup(html, "html.parser")  # 格式化爬取的页面数据
    return soup.find(id='list-container').find('ul', {'class': 'note-list'})  # 文章列表

def crawl_paper_tag(list, url_root):
    """
    获取文章列表详情
    :param list: 要爬取的文章列表
    :param url_root: 爬取网站的根目录
    :return:
    """
    paperList = [] # 文章属性集列表
    lists = list.find_all('li')
    # print (lists)
    for paperTag in lists:
        author = paperTag.find('div', {'class': 'content'}).find('a', {'class': 'blue-link'}).text # 作者
        title = paperTag.find('div', {'class': 'content'}).find('a', {'class': 'title'}).text # 标题
        paperURL = paperTag.find('div', {'class': 'content'}).find('a', {'class': 'title'}).get('href') # 文章网址
        abstract = paperTag.find('div', {'class': 'content'}).find('p', {'class': 'abstract'}).text # 文章摘要
        if paperTag.find('a', {'class': 'wrap-img'}) != None:
            pic = paperTag.find('a', {'class': 'wrap-img'}).find('img').get('src') # 文章缩略图
        else:
             pic = 'No Pic'
        metaRead = paperTag.find('div', {'class': 'content'}).find('i', {'class': 'iconfont ic-list-read'}).find_parent('a').text # 阅读数
        metaComment = paperTag.find('div', {'class': 'content'}).find('i', {'class': 'iconfont ic-list-comments'}).find_parent('a').text # 评论数
        metaLike = paperTag.find('div', {'class': 'content'}).find('i', {'class': 'iconfont ic-list-like'}).find_parent('span').text # 点赞数
        if paperTag.find('div', {'class': 'content'}).find('i', {'class': 'iconfont ic-list-money'}) != None:
            metaReward =  paperTag.find('div', {'class': 'content'}).find('i', {'class': 'iconfont ic-list-money'}).find_parent('span').text# 打赏数
        else:
            metaReward = 0
        paperAttr = {
            'author': author,
            'title': title,
            'url': urlparse.urljoin(url_root, paperURL),
            'abstract': abstract,
            'pic': pic,
            'read': metaRead,
            'comment': metaComment,
            'like': metaLike,
            'reward': metaReward
        }
        # print (paperAttr['title'])
        write_file(title, paperAttr)
        paperList.append(paperAttr)
    return paperList

def write_file(title, paperattr):
    if os.path.exists('spider_output/') == False:  # 检查保存文件的地址
        os.mkdir('spider_output/')
    cleaned_title = clean_title(title)
    file_name = 'spider_output/' + cleaned_title + '.txt' #设置要保存的文件名  # 设置要保存的文件名
    # if os.path.exists(file_name):
        # os.remove(file_name) # 删除文件
        # return  # 已存在的文件不再写
    file = open(file_name, 'wb')
    content =  'Author:' + (unicode(paperattr['author']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Title:' + (unicode(paperattr['title']).encode('utf-8', errors='ignore')) + '\n' \
               + 'URL:' + (unicode(paperattr['url']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Abstract:' + (unicode(paperattr['abstract']).encode('utf-8', errors='ignore')) + '\n' \
               + 'ArtilcePic:' + (unicode(paperattr['pic']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Read:' + (unicode(paperattr['read']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Comment:' + (unicode(paperattr['comment']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Like:' + (unicode(paperattr['like']).encode('utf-8', errors='ignore')) + '\n' \
               + 'Reward:' + (unicode(paperattr['reward']).encode('utf-8', errors='ignore')) + '\n'
    file.write(content)
    file.close()

def clean_title(title):
    """
    替换特殊字符，否则根据文章标题生成文件名的代码会运行出错
    """
    title = title.replace('|', ' ')
    title = title.replace('"', ' ')
    title = title.replace('/', ',')
    title = title.replace('<', ' ')
    title = title.replace('>', ' ')
    title = title.replace('\x08', '')
    return title

def crawl_papers(url_seed, url_root):
    """
    抓取所有的文章列表
    :param url_seed: 下载的种子页面地址
    :param url_root: 爬取网站的根目录
    :return:
    """
    i = 1
    flag = True  # 标记是否需要继续爬取
    while flag:
        url = url_seed % i  # 真正爬取的页面
        i += 1  # 下一次需要爬取的页面
        article_list = crawl_list(url)  # 下载文章列表
        article_tag = crawl_paper_tag(article_list, url_root)
        # print (article_tag)
        if article_tag.__len__() == 0:  # 下载文章列表返回长度为0的列表，表示已爬取到最后
            flag = False

url_root = 'http://www.jianshu.com/'
url_seed = 'http://www.jianshu.com/c/9b4685b6357c/?order_by=added_at&page=%d'
crawl_papers(url_seed, url_root)
