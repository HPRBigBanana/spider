""""""
"""
采用生产者与消费者模式！
（注意：该数据保存至csv文件当中时，出现乱码，后续再解决）

"""
import requests
from lxml import etree
import threading
from queue import Queue
import csv

"""0. 创建一个继承了“threading.Thread类”的生产者类"""
class BSSpider(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    """1. 在BSSpider类中重写threading.Thread类中 __init__函数
             来给BSSpider类赋予属性
             并且通过“*args,**kwargs”这两个参数来代表“threading.Thread类”中
             原本的所有参数。
       """
    def __init__(self,page_queue,joke_queue,*args,**kwargs):
        """"""
        """2. 想要进行重写，必须通过super调用父类threading.Thread类中的init函数
                      并将“*args,**kwargs”传给父类
        """
        super(BSSpider, self).__init__(*args,**kwargs)
        self.base_domain = 'http://www.budejie.com'
        self.page_queue = page_queue
        self.joke_queue = joke_queue

    """3. 对我们所继承的“threading.Thread类”中的run()方法进行重写/进行覆盖。
              当我们创建该类对象时，比如 t1 = BSSpider()；
              （由于该类继承了“threading.Thread类”）
              t1 就是一个“线程”
              t1.start() 就会自动调用run()方法
    """
    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            response = requests.get(url, headers=self.headers)
            text = response.text
            html = etree.HTML(text)
            descs = html.xpath("//div[@class='j-r-list-c-desc']")
            for desc in descs:
                jokes = desc.xpath(".//text()")
                joke = "\n".join(jokes).strip()
                link = self.base_domain+desc.xpath(".//a/@href")[0]
                self.joke_queue.put((joke,link))
            print('='*30+"第%s页下载完成！"%url.split('/')[-1]+"="*30)

class BSWriter(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    def __init__(self, joke_queue, writer,gLock, *args, **kwargs):
        super(BSWriter, self).__init__(*args, **kwargs)
        self.joke_queue = joke_queue
        self.writer = writer

        """4. 设置一个锁对象"""
        self.lock = gLock

    def run(self):
        while True:
            try:
                joke_info = self.joke_queue.get(timeout=40)
                joke,link = joke_info
                self.lock.acquire()
                self.writer.writerow((joke,link))
                self.lock.release()
                print('保存一条')
            except:
                break

def main():
    page_queue = Queue(10)
    joke_queue = Queue(500)
    gLock = threading.Lock()

    """保存位置"""
    fp = open('G:/python_project/文件保存/bsbdj.csv', 'a',newline='', encoding='utf-8')
    writer = csv.writer(fp)
    writer.writerow(('content', 'link'))

    for x in range(1,11):
        url = 'http://www.budejie.com/text/%d' % x
        page_queue.put(url)

    for x in range(5):
        t = BSSpider(page_queue,joke_queue)
        t.start()

    for x in range(5):
        t = BSWriter(joke_queue,writer,gLock)
        t.start()

if __name__ == '__main__':
    main()
