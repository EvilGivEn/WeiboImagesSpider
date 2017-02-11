#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import re
import os.path
import sys
import time
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboSpider():
    
    def __init__(self, Cookie, OneUser):

        self.Header = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie':Cookie,
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
        }
        self.Name   = OneUser['name']
        self.Path   = './WeiboImages/' + OneUser['name'] + '/'
        self.Uid    = OneUser['uid']
        self.Url    = 'http://weibo.cn/u/' + self.Uid
        self.Img    = []
        self.Tol    = 0
        self.Start  = OneUser['start']
        self.InPage = self.Start
        self.End    = 1

        if not os.path.exists(self.Path):
            os.makedirs(self.Path)

        try:
            html = requests.get(url = self.Url + '?filter=1&page=1', headers = self.Header)
        except:
            self.ContentBanned(Error = u'网络连接错误, 请稍后再试')

        while html.status_code != 200:

            if html.status_code == 403:

                self.ContentBanned()

            elif html.status_code == 404:

                print u'错误的微博uid'
                print u'当前抓取微博uid为 ' + OneUser['uid'] + u' 保存在 ' + OneUser['name'] + u'文件夹内'
                Uid     = raw_input(u'输入一个新的微博uid(按[回车]跳过当前微博): '.decode('utf-8').encode('gbk'))
                if Uid  == '': self.IgnoreUser()

                while True:
                    Name = raw_input(u'输入一个文件夹名来存储该微博的图片(按[回车]使用原文件夹名): '.decode('utf-8').encode('gbk')).decode(sys.stdin.encoding)
                    temp = re.findall(r'[\/*?"<>|]', Name)

                    if len(temp) > 0:
                        print u'文件夹名非法, 请不要包含\ / * ? " < > | 这些字符'

                    else:
                        if Name == '':
                            OneUser = {'name':Name, 'uid':Uid, 'start':0}
                        else:
                            OneUser = {'name':self.Name, 'uid':Uid, 'start':0}

            else:
                self.ContentBanned(Error = u'网络连接错误, 请稍后再试')

            try:
                html = requests.get(url = self.Url + '?filter=1&page=1', headers = self.Header)
            except:
                self.ContentBanned(Error = u'网络连接错误, 请稍后再试')

        temp0 = re.findall(r'&nbsp;\d+/\d+', html.content)

        if len(temp0) > 0:

            temp1    = re.findall(r'\d+', temp0[0])
            self.End = int(temp1[1])

        print u'当前微博共 ' + str(self.End) + u' 页'

        
    def LoadPage(self, PageNo):

        url = self.Url + '?filter=1&page=' + str(PageNo)

        print u'正在载入第 ' + str(PageNo) + u' 页 [' + url + u']'

        self.InPage = PageNo

        try:
            ReqGet = requests.get(url = url, headers = self.Header)
        except:
            self.ContentBanned(Error = u'网络连接错误, 请稍后再试')

        if ReqGet.status_code == 403:

            self.ContentBanned()

        else:
            return ReqGet.content


    def ProcessData(self, HtmlPage):

        print u'获取当前页面图片链接'

        Soup     = BeautifulSoup(HtmlPage, 'lxml')
        UrlList0 = Soup.find_all('a', href = re.compile(r'^http://weibo.cn/mblog/oripic', re.I))
        UrlList1 = Soup.find_all('a', href = re.compile(r'^http://weibo.cn/mblog/picAll', re.I))

        for Outer in UrlList0:

            temp = re.findall(r'\w{32}', Outer['href'])

            if len(temp) > 0 and not os.path.isfile(self.Path + temp[0] + '.jpg'):

                Outer['href'] = re.sub(r"amp;", '', Outer['href'])
                self.Img     += [{"url":Outer['href'], "path":self.Path + temp[0] + '.jpg'}]

                print u'找到一个图片链接 [' + Outer['href'] + u']'

            time.sleep(0.1)

        for Outer in UrlList1:

            try:
                ReqGet = requests.get(url = Outer['href'], headers = self.Header)
            except:
                self.ContentBanned(Error = u'网络连接错误, 请稍后再试')

            Soup     = BeautifulSoup(ReqGet.content, 'lxml')
            UrlList2 = Soup.find_all('a', href = re.compile(r'^/mblog/oripic', re.I))

            time.sleep(0.1)

            for Inner in UrlList2:

                temp = re.findall(r'\w{32}', Inner['href'])

                if len(temp) > 0 and not os.path.isfile(self.Path + temp[0] + '.jpg'):

                    Inner['href'] = 'http://weibo.cn' + re.sub(r'amp;', '', Inner['href'])
                    self.Img     += [{'url':Inner['href'], 'path':self.Path + temp[0] + '.jpg'}]

                    print u'找到一个图片链接 [' + Inner['href'] + u']'

        
    def GetImageInfo(self):

        print u'\n开始抓取图片链接\n'

        Start = self.Start

        if Start > self.End: return

        for i in range(self.End - Start + 1):

            print u'\n正在抓取第 ' + str(i + Start) + u' 页的图片链接, 共 ' + str(self.End) + u' 页'

            self.ProcessData(self.LoadPage(PageNo = i + Start))

            print u'第 ' + str(i + Start) + u' 页的图片链接抓取完毕, 等待 5 秒...'
            time.sleep(5)

            if len(self.Img) >= 50:

                self.DownImages()
                self.Tol += len(self.Img)
                self.Img = []

        self.Tol += len(self.Img)

        print u'全部图片链接获取完毕， 等待 60 秒...'
        time.sleep(60)


    def SaveImage(self, ImagePath, Content):

        if os.path.isfile(ImagePath):

            print u'图片 ' + ImagePath + u' 已存在'

        else:
            with open(ImagePath, 'wb') as fp:
                fp.write(Content)

            print u'图片 ' + ImagePath + u' 保存成功'


    def DownImages(self):

        print u'\n开始下载 ' + str(len(self.Img)) + u' 张图片\n'

        for i, image in enumerate(self.Img):

            print u'正在下载第 ' + str(i + 1) + u' 张图片'

            try:
                req = requests.get(url = image['url'], headers = self.Header)
            except:
                self.ContentBanned(Error = u'网络连接错误, 请稍后再试')
            
            if req.status_code == 403:
                self.ContentBanned()

            print u'正在保存图片 ' + image['path']

            self.SaveImage(ImagePath = image['path'], Content = req.content)

            time.sleep(1)

        print str(len(self.Img)) + u' 张图片以下载完毕， 等待 30 秒...'
        time.sleep(30)


    class Banned(Exception):

        def __init__(self, Uid, Name, Page, Error):

            Exception.__init__(self, Error)

            self.Uid  = Uid
            self.Name = Name
            self.Page = Page


    def ContentBanned(self, Error = u'这个Cookie被限制了, 请换一个Cookie.'):

        print Error
        raise self.Banned(Uid = self.Uid, Name = self.Name, Page = self.InPage, Error = Error)


    class Ignore(Exception):

        def __init__(self):

            Exception.__init__(self)


    def IgnoreUser(self):

        print '微博uid ' + self.Uid + ' 已跳过'
        raise self.Ignore()