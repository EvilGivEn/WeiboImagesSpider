# WeiboImagesSpider
Python 写的微博定向抓取图片的爬虫

使用Cookie通过weibo.cn抓取指定微博用户的全部图片

简明使用指南

  0) 获取微博的Cookie
  
  以Chrome为例， 打开 www.weibo.com 在未登陆的情况下按F12开启浏览器的开发者模式再登陆微博, 在Network页点击 weibo.com (weibo.cn) 查看Headers
  Headers里的Cookie项就是我们要用到的Cookie, 如果提示Cookie被限制请更换账号重复上述步骤或者等待一段时间微博自动解除限制
  
  1) 输入微博uid
  
  与每一个微博一一对应的特定的一串数字, 可以在微博图片水印的链接或微博主页的像 weibo/u/xxxxxxxx 的链接中找到, xxxxxxxx 即为uid
  
  2) 输入目录名
  
  输入一个文件夹名来保存该微博的图片, 不是路径名, 文件夹如果不存在则会自动新建文件夹, 抓取到的图片保存在 ./WeiboImages/ [你输入的文件名] / 目录下
  
  3) 多个微博
  
  如果需要一次抓取多个微博, 重复步骤 1 ~ 2 即可
  爬虫支持断点续传, 如果在抓取过程中遇到网络问题退出爬虫(如Cookie被限制) 再次启动爬虫并输入Cookie后即可自动继续最后一次未完成的抓取
