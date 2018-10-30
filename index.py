import tornado.ioloop
import tornado.web
import pymysql
from datetime import datetime
from bs4 import BeautifulSoup

from tornado import httpclient

KEYWORD = "아이유"
GITHUB_TRENDING_URL = "https://github.com/trending"

CONN = pymysql.connect(host='localhost',
                       user='whale',
                       password='pass',
                       db='whale_db',
                       charset='utf8')


async def get_trend_repo_title(url):
    request = httpclient.HTTPRequest(
        url=url,
        method="GET",
        headers={
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
    )

    response = await httpclient.AsyncHTTPClient().fetch(request)
    html = response.body.decode(errors='ignore')
    soup = BeautifulSoup(html, "html.parser")

    return list(map((lambda x: x.text.strip()), soup.select(".repo-list > li h3")))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("crawler!")


class CrawlTitle(tornado.web.RequestHandler):

    async def get(self):
        titles = await get_trend_repo_title(GITHUB_TRENDING_URL)
        for i, title in enumerate(titles, start=1):
            self.write("{index}. {title} <br/>".format(index=i, title=title))

        today = datetime.now().date()
        delete_repos(today)
        insert_repos(titles)


class GetTitle(tornado.web.RequestHandler):

    def get(self):
        today = datetime.now().date()
        for id, rank, title, date in get_repos(today):
            self.write("{index}. {title} <br/>".format(index=rank, title=title))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/crawl", CrawlTitle),
        (r"/rank", GetTitle),
    ])


def init_database():
    if not check_table_exist("repos"):
        create_table()


def check_table_exist(table_name):
    exist = False
    with CONN.cursor() as cursor:
        sql = '''SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}';'''.format(table_name)
        cursor.execute(sql)
        if cursor.fetchone()[0] == 1:
            exist = True
    return exist


def create_table():
    with CONN.cursor() as cursor:
        sql = '''
         CREATE TABLE repos (
            id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
            ranking int(2) NOT NULL,
            name varchar(255) NOT NULL,
            datetime datetime NOT NULL
        ) ENGINE=InnoDB'''
        cursor.execute(sql)
    CONN.commit()


def insert_repos(repo_list):
    with CONN.cursor() as cursor:
        sql = '''
         INSERT INTO `whale_db`.`repos` (`ranking`, `name`, `datetime`) 
         VALUES (%s, %s, %s);'''
        today = datetime.now().date()
        cursor.executemany(sql, list(map(lambda x: x + (today,), enumerate(repo_list))))
    CONN.commit()


def delete_repos(date):
    with CONN.cursor() as cursor:
        sql = '''DELETE FROM `whale_db`.`repos` WHERE `datetime` = %s;'''
        cursor.execute(sql, date)
    CONN.commit()


def get_repos(date):
    with CONN.cursor() as cursor:
        sql = '''select * from whale_db.repos where `datetime` = %s;'''
        cursor.execute(sql, date)
        return cursor.fetchall()


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    init_database()
    tornado.ioloop.IOLoop.current().start()
