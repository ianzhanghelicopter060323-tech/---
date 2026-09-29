"""A tiny local website used for crawler practice."""

from flask import Flask, render_template


app = Flask(__name__)

ARTICLES = [
    {
        "title": "Python 爬虫入门",
        "author": "小林",
        "summary": "使用 requests 获取网页，再用 BeautifulSoup 解析 HTML。",
        "category": "Python",
        "year": 2022,
        "word_count": 1200,
        "views": 860,
    },
    {
        "title": "认识 Flask",
        "author": "小周",
        "summary": "用一个最小的 Web 应用提供可供练习的本地页面。",
        "category": "Web 开发",
        "year": 2023,
        "word_count": 1800,
        "views": 1350,
    },
    {
        "title": "尊重 robots.txt",
        "author": "小陈",
        "summary": "抓取真实网站前，应先确认网站规则并控制请求频率。",
        "category": "Python",
        "year": 2023,
        "word_count": 950,
        "views": 720,
    },
    {
        "title": "BeautifulSoup 选择器",
        "author": "小林",
        "summary": "从表格中定位行和单元格，提取需要的数据。",
        "category": "Python",
        "year": 2024,
        "word_count": 2100,
        "views": 1920,
    },
    {
        "title": "HTML 表格结构",
        "author": "小周",
        "summary": "认识 table、thead、tbody、tr 和 td 标签。",
        "category": "Web 开发",
        "year": 2022,
        "word_count": 1300,
        "views": 980,
    },
    {
        "title": "用 JSON 保存数据",
        "author": "小陈",
        "summary": "将爬取到的文章信息写入 JSON 文件。",
        "category": "数据分析",
        "year": 2024,
        "word_count": 1600,
        "views": 1450,
    },
    {
        "title": "统计文章分类",
        "author": "小林",
        "summary": "统计每个分类的文章数量并绘制柱状图。",
        "category": "数据分析",
        "year": 2025,
        "word_count": 2400,
        "views": 2300,
    },
    {
        "title": "Flask 模板基础",
        "author": "小周",
        "summary": "使用模板循环渲染多条文章记录。",
        "category": "Web 开发",
        "year": 2025,
        "word_count": 1700,
        "views": 1680,
    },
    {
        "title": "浏览量区间分析",
        "author": "小陈",
        "summary": "将浏览量分组，观察不同区间的文章分布。",
        "category": "数据分析",
        "year": 2025,
        "word_count": 2000,
        "views": 2050,
    },
]

@app.get("/")
def index():
    return render_template("index.html", articles=ARTICLES)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
