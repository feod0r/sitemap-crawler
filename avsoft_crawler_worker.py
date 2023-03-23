import requests
import re
import time
import pandas as pd
import threading
from sqlalchemy import create_engine

site = input('Сайт для создания карты: ')
use_subdomains = False
max_depth = 10000
#настройка базы данных
hostname="localhost"
dbname="vasoft"
uname="root"
pwd="password"

def timer(func):
    t1 = time.time();
    func();
    t2 = time.time() -t1;
    print('\n======================')
    print(f'Run tooks {t2} seconds')
    print('======================')
    
    
class endpoint:
    def __init__(self, site, link, status, title):
        self.site = site
        self.link = link
        self.status = status
        self.title = title
        
class crawler:
    
    def __init__(self,link):
        self.success = {}
        self.to_crawl = [link]
        self.domain = re.search(r'https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b)',link).group(2)
        
        
    def worker(self,number):
        while len(self.to_crawl) > 0+number-1 and len(self.success) < max_depth:
            print('\r Got {} out of {} worker {}         '.format(len(self.success),len(self.to_crawl),number), end='')
            self.crawl_link(self.to_crawl[0+number-1])
        
    def crawl_link(self,link):
        
        
        if self.success.get(link):
            self.remove_link(link)
            return 0
        domain = re.search(r'https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b)',link)
        
        
        try:
            response = requests.get(link, allow_redirects=True,  timeout=7)
            body = response.text
            status = response.status_code
            #сохранение заголовка
            title = ''.join(re.findall(r'<title>([^<]*)</title>',body))
            #поиск ссылок только в теле
            body = body.split('<body>',1)[1] if len(body.split('<body>',1))>1 else body
        except Exception as e:
            print("Error Link: ", link)
            print("Error Name: ", e.__class__.__name__)
            print("Error Message: ", e)
            self.success[link] = endpoint(domain.group(0), link, 0, '')
            self.remove_link(link)
            return 0 
            
        if status == 200:
            self.to_crawl += self.get_links(domain, body)
        self.success[link] = endpoint(domain.group(0), link, status, title)
        self.remove_link(link)
        
        
    def get_links(self, domain, body):
        raw_links = re.findall(r'href="([^"]*)"',body)
        links = []
        for row in raw_links:
            result = re.search(r'https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4})\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',row)
            #проверка что это вообще ссылка
            if result:
                if use_subdomains:
                    #проверка что ссылка находится в том же домене
                    if result.group(0).find(self.domain) > -1:
                         links.append(result.group(0))
                         #print(result.group(0),domain.group(2), self.domain)
                else:
                    #проверка что ссылка находится в том же домене и бех субдомена
                    if result.group(2) == self.domain:
                        #print(result.group(0),domain.group(2), self.domain)
                        #добавление глобальных ссылок
                        links.append(result.group(0))
            else:
                #добавление относительных ссылок
                if len(row)>0:
                    links.append(domain.group(0) + '/' + (row[1:] if row[0]=='/' else row))

        return links
    
    
    def start_task(self):
        procs = []
        count = 0
        print('Warmup...')
        for i in range(30):
            self.crawl_link(self.to_crawl[len(self.to_crawl)-1])
        print('Warmup done')
        
        for address in range(0,50):
            procs.append(threading.Thread(target=self.worker, args=(address,)))
        for thread in procs:
            thread.start()  # каждый поток должен быть запущен
        for thread in procs:
            thread.join()  # дожидаемся исполнения всех потоков
        procs.clear()

    
    def get_success(self):
        result = pd.DataFrame([
            [self.success[key].site, self.success[key].link, self.success[key].status, self.success[key].title]
            for key in self.success.keys()],
            columns=['site','link','status','title'])
        return result
    
    
    def remove_link(self,link):
        try:
            self.to_crawl.remove(link)
        except Exception as e:
            pass
        
        
        
crw = crawler(site)
timer(crw.start_task)




# Create SQLAlchemy engine to connect to MySQL Database
engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))
                            
print('Inserted {} rows to db.'.format(crw.get_success().to_sql('sitemap', engine, index=False, if_exists='append')))
crw.get_success().to_csv(crw.domain+ '.csv')  
