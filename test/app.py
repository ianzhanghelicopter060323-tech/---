"""A tiny local website used for crawler practice."""

from flask import Flask, render_template_string


app = Flask(__name__)

ARTICLES = [
    {
        "title": "Python 爬虫入门",
        "author": "小林",
        "summary": "使用 requests 获取网页，再用 BeautifulSoup 解析 HTML。",
    },
    {
        "title": "认识 Flask",
        "author": "小周",
        "summary": "用一个最小的 Web 应用提供可供练习的本地页面。",
    },
    {
        "title": "尊重 robots.txt",
        "author": "小陈",
        "summary": "抓取真实网站前，应先确认网站规则并控制请求频率。",
    },
]

PAGE_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>本地爬虫练习站</title>
</head>
<body>
  <h1 id="site-title">本地爬虫练习站</h1>
  <div id="articles">
    {% for article in articles %}
    <article class="article-card">
      <h2 class="title">{{ article.title }}</h2>
      <p class="author">作者：<span>{{ article.author }}</span></p>
      <p class="summary">{{ article.summary }}</p>
    </article>
    {% endfor %}
  </div>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE_TEMPLATE, articles=ARTICLES)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
