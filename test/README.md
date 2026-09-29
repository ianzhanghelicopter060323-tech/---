# 本地爬虫测试

> 为的是在不考虑反爬机制的情况下测试爬取结果 

先在项目根目录安装依赖：

```bash
python3 -m pip install -r test/requirements.txt
```

打开第一个终端，启动本地网站：

```bash
python3 test/app.py
```

保持网站运行，再打开第二个终端执行爬虫：

```bash
python3 test/crawler.py
```

浏览器也可以直接访问 <http://127.0.0.1:5000/> 查看被抓取的页面。
