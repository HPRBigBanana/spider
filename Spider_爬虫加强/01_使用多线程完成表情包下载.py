#encoding: utf-8

import requests
from lxml import etree
from urllib import request
import os
import re
from queue import Queue
import threading

"""0. 创建一个继承了“threading.Thread类”的生产者类"""
class Procuder(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    """1. 在Procuder类中重写threading.Thread类中 __init__函数
          来给Procuder类赋予属性
          并且通过“*args,**kwargs”这两个参数来代表“threading.Thread类”中
          原本的所有参数。
    """
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        """"""
        """2. 想要进行重写，必须通过super调用父类threading.Thread类中的init函数
              并将“*args,**kwargs”传给父类
        """
        super(Procuder, self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    """3. 对我们所继承的“threading.Thread类”中的run()方法进行重写/进行覆盖。
          当我们创建该类对象时，比如 t1 = CodingThread()；
          （由于该类继承了“threading.Thread类”）
          t1 就是一个“线程”
          t1.start() 就会自动调用run()方法
    """
    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_page(url)

    def parse_page(self,url):
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")
        for img in imgs:
            img_url = img.get('data-original')
            alt = img.get('alt')
            alt = re.sub(r'[\?？\.，。！!\*]','',alt)
            suffix = os.path.splitext(img_url)[1]
            filename = alt + suffix
            self.img_queue.put((img_url,filename))


"""0.1. 创建一个继承了“threading.Thread类”的消费者类"""
class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer, self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            img_url,filename = self.img_queue.get()

            """request.urlretrieve(想要下载的东西的url地址,保存位置) """
            request.urlretrieve(img_url,'images/'+filename)
            print(filename+'  下载完成！')


def main():
    page_queue = Queue(100)
    img_queue = Queue(1000)
    for x in range(1,101):
        url = 'http://www.doutula.com/photo/list/?page={}'.format(x)
        page_queue.put(url)

    for x in range(5):
        t = Procuder(page_queue,img_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue,img_queue)
        t.start()


if __name__ == '__main__':
    main()