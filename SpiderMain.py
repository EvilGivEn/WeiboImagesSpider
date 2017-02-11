#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import re
import os.path
import sys
import time
import json

from SpiderClass import WeiboSpider

reload(sys)
sys.setdefaultencoding('utf-8')

Users = []

SavePath = './BreakPoint.json'
MODE = 'REAL'

print u"\n========================爬虫设置=========================="

Cookie = raw_input(u'请输入一个有效的Cookie: '.decode('utf-8').encode('gbk'))

header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Cookie':Cookie,
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
}

temp = requests.get(url = 'http://weibo.cn/u/1916825084?filter=1&page=1', headers = header)

while temp.status_code != 200:

    if temp.status_code == 403:

        print u'这个Cookie被限制了, 请换一个Cookie.'

        Cookie = raw_input(u'请输入一个有效的Cookie(按[回车]键退出爬虫): '.decode('utf-8').encode('gbk'))
        if Cookie == '': sys.exit(0)
        header['Cookie'] = Cookie

        temp = requests.get(url = 'http://weibo.cn/u/1916825084?filter=1&page=1', headers = header)

    else:

        print u'网络连接错误, 请稍后再试'
        sys.exit(0)

if os.path.isfile(SavePath):

    op = raw_input(u'输入[Y]继续上次未完成的任务: '.decode('utf-8').encode('gbk'))

    if op == 'Y' or op == 'y':

        MODE = 'LOAD'

        print u'加载中...'

        try:

            fp    = open(SavePath)
            Users = json.load(fp)

        except:

            print u'加载错误, 正在退出...'

            try:
                fp.close()
                os.remove(SavePath)
            except:
                pass

            sys.exit(0)

        finally:

            try:
                fp.close()
                os.remove(SavePath)
            except:
                pass

        print u'加载完毕, 共 ' + str(len(Users)) + u' 条信息'

        for i in range(len(Users)):
            print u'微博uid ' + Users[i]['uid'] + u' 存储在 ' + Users[i]['name'] + u' 目录下， 从第 ' + str(Users[i]['start']) + u' 页开始'

if MODE == 'REAL':

    Uid     = raw_input(u'请输入一个微博uid: '.decode('utf-8').encode('gbk'))

    while True:

        Name = raw_input(u'输入一个文件夹名来存储该微博的图片: '.decode('utf-8').encode('gbk')).decode(sys.stdin.encoding)
        temp = re.findall(r'[\/*?"<>|]', Name)
        
        if len(temp) > 0:
            print u'文件夹名非法, 请不要包含\ / * ? " < > | 这些字符'
        else:
            break

    Users  += [{'name':Name, 'uid':Uid, 'start':1}]

    while True:

        Uid    = raw_input(u'请输入一个微博uid(按[回车]结束输入): '.decode('utf-8').encode('gbk'))
        if Uid == '': break

        while True:
            Name = raw_input(u'输入一个文件夹名来存储该微博的图片: '.decode('utf-8').encode('gbk')).decode(sys.stdin.encoding)
            temp = re.findall(r'[\/*?"<>|]', Name)
            if len(temp) > 0:
                print u'文件夹名非法, 请不要包含\ / * ? " < > | 这些字符'
            else:
                break

        Users += [{'name':Name, 'uid':Uid, 'start':1}]

print u"\n========================爬虫开始========================="

for i in range(len(Users)):

    try:

        Spider = WeiboSpider(Cookie = Cookie, OneUser = Users[0])
        Spider.GetImageInfo()
        Spider.DownImages()

        Users.remove(Users[0])

    except Spider.Banned as Err:

        Users[0] = {
            'name':Err.Name, 
            'uid':Err.Uid,
            'start':Err.Page
        }

        if os.path.isfile(SavePath):

            op = raw_input(u'已经存在一个未完成的任务, 按[Y]覆盖这个任务: '.decode('utf-8').encode('gbk'))

            if op == 'Y' or op == 'y':

                with open(SavePath, 'w') as fp:
                    fp.write(json.dumps(Users))

            else:
                print u'退出爬虫...'

        else:

            with open(SavePath, 'w') as fp:
                fp.write(json.dumps(Users))

        sys.exit()

    except Spider.Ignore:

        print u'等待 30 秒'
        time.sleep(30)

        continue

    print u'微博 ' + Users[0]['uid'] + u' 抓取完毕, 等待 300 秒防止访问过于频繁'
    time.sleep(300)

if MODE == 'LOAD':

    try:
        os.remove(SavePath)
    except:
        pass

print u'\n========================爬虫结束========================='