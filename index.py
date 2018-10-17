import tornado.ioloop
import tornado.web
from bs4 import BeautifulSoup

from tornado import httpclient

KEYWORD = "아이유"
GITHUB_TRENDING_URL = "https://github.com/trending"

def save_title(titles):
    pass

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


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/crawl", CrawlTitle),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
